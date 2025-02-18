"""
Enhanced MCP Server Implementation with Interface Support

Provides:
- Comprehensive session and transport management
- Protocol version handling
- Robust error handling and logging
- Enhanced health monitoring
- Integration with interface contracts
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union, Callable, AsyncGenerator
import sys
import os
import signal
import psutil
from datetime import datetime, timezone
from dataclasses import dataclass

from .shared_types import (
    MCPVersion,
    ProtocolError,
    ErrorCodes,
    TransportType,
    ComponentState,
    PROTOCOL_VERSION,
    MINIMAL_COMPATIBLE_VERSION,
    MetricsData,
    MessageStream
)
from .initialization import ServerInitializer
from .interfaces import (
    ServerInterface,
    ConnectionInterface,
    TransportInterface,
    OptimizerInterface,
    ProtocolInterface,
    SessionInterface,
    ConversationHandlerInterface,
    RateLimiterInterface,
    MetricsInterface
)
from .rate_limiter import AdaptiveRateLimiter, RateLimitRule
from .utils.json_utils import dumps_with_datetime, loads_with_datetime

@dataclass
class MetricsVersion:
    """Track metrics structure version."""
    MAJOR = 1
    MINOR = 0
    PATCH = 0

    @classmethod
    def to_string(cls) -> str:
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"


class MCPServer(ServerInterface):
    """Enhanced MCP Server implementation."""

    PROTOCOL_VERSION: MCPVersion = MCPVersion.parse(PROTOCOL_VERSION)
    """Current protocol version of the server."""
    HEALTH_CHECK_DEFAULT: int = 60
    """Default interval in seconds for health checks."""

    def __init__(
        self,
        config: Dict[str, Any],
        logger: logging.Logger,
        protocol_handler: ProtocolInterface,
        session_manager: Optional[SessionInterface] = None,
        transport_manager: Optional[TransportInterface] = None,
        connection_manager: Optional[ConnectionInterface] = None,
        conversation_handler: Optional[ConversationHandlerInterface] = None,
        optimizer: Optional[OptimizerInterface] = None,
        metrics_collector: Optional[MetricsInterface] = None
    ):
        """Initialize the server with required components."""
        self.logger = logger
        self.config = config
        self.protocol_handler = protocol_handler
        self.session_manager = session_manager
        self.transport_manager = transport_manager
        self.connection_manager = connection_manager
        self.conversation_handler = conversation_handler
        self.optimizer = optimizer
        self.metrics_collector = metrics_collector

        # Basic state
        self.initialized: bool = False
        self.shutdown_event = asyncio.Event()
        self.start_time = datetime.now(timezone.utc)
        self.pid = os.getpid()

        # Component state tracking
        self.component_state = ComponentState.UNINITIALIZED

        # Rate limiter setup
        rate_limit_config = self.config.get('rate_limiter', {})
        self.rate_limiter = AdaptiveRateLimiter(
            default_rule=RateLimitRule(
                tokens_per_second=rate_limit_config.get('tokens_per_second', 1.0),
                burst_size=rate_limit_config.get('burst_size', 2)
            )
        )

        # Metrics tracking
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
            "rate_limited_requests": 0,
            "active_sessions": 0,
            "streaming_metrics": {
                "total_streams": 0,
                "active_streams": 0,
                "failed_streams": 0
            }
        }

        # Health check
        self._health_check_task: Optional[asyncio.Task] = None
        self.health_check_interval = self.config.get("health_check_interval", 60)
        self._last_health_check = datetime.now(timezone.utc)

    @classmethod
    async def create(cls, config: Dict[str, Any], logger: logging.Logger) -> 'MCPServer':
        """Factory method to handle initialization order."""
        initialized_components = await ServerInitializer.create_server(config, logger)

        # Add type validation
        optimizer = initialized_components['optimizer']
        if not isinstance(optimizer, OptimizerInterface):
            raise TypeError("Optimizer must implement OptimizerInterface")

        protocol_handler = initialized_components['protocol_handler']
        if not isinstance(protocol_handler, ProtocolInterface):
            raise TypeError("Protocol handler must implement ProtocolInterface")

        session_manager = initialized_components['session_manager']
        if not isinstance(session_manager, SessionInterface):
            raise TypeError("Session manager must implement SessionInterface")

        transport_manager = initialized_components['transport_manager']
        if not isinstance(transport_manager, TransportInterface):
            raise TypeError("Transport manager must implement TransportInterface")

        connection_manager = initialized_components['connection_manager']
        if not isinstance(connection_manager, ConnectionInterface):
            raise TypeError("Connection manager must implement ConnectionInterface")

        conversation_handler = initialized_components['conversation_handler']
        if conversation_handler and not isinstance(conversation_handler, ConversationHandlerInterface):
            raise TypeError("Conversation handler must implement ConversationHandlerInterface")

        metrics_collector = initialized_components.get('metrics_collector')
        if metrics_collector and not isinstance(metrics_collector, MetricsInterface):
            raise TypeError("Metrics collector must implement MetricsInterface")

        server = cls(
            config=config,
            logger=logger,
            protocol_handler=protocol_handler,
            session_manager=session_manager,
            transport_manager=transport_manager,
            connection_manager=connection_manager,
            conversation_handler=conversation_handler,
            optimizer=optimizer,
            metrics_collector=metrics_collector
        )

        if not await server.initialize():
            raise ProtocolError(
                "Server initialization failed",
                ErrorCodes.SERVER_NOT_INITIALIZED
            )

        return server

    async def initialize(self) -> bool:
        """Initialize server components."""
        if self.initialized:
            return True

        try:
            # Update component state
            self.component_state = ComponentState.INITIALIZING

            # Verify protocol version compatibility
            protocol_version = self.config.get("MCP_PROTOCOL_VERSION", MINIMAL_COMPATIBLE_VERSION)
            version = MCPVersion.parse(protocol_version)
            if not version.is_compatible(MINIMAL_COMPATIBLE_VERSION):
                raise ProtocolError(
                    f"Protocol version {protocol_version} not compatible with {MINIMAL_COMPATIBLE_VERSION}",
                    ErrorCodes.VERSION_MISMATCH
                )

            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._monitor_server_health())

            # Start metrics collection
            if self.metrics_collector:
                await self.metrics_collector.start()

            self.initialized = True
            self.component_state = ComponentState.READY
            self.logger.info("MCP Server fully initialized and ready.")
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Server initialization failed: {e}")
            await self._cleanup_partial_initialization()
            raise ProtocolError(
                f"Initialization failed: {e}",
                ErrorCodes.SERVER_NOT_INITIALIZED
            )

    async def _cleanup_partial_initialization(self):
        """Clean up components that were initialized if initialization partially failed."""
        cleanup_errors = []
        components = [
            ('connection_manager', self.connection_manager),
            ('transport_manager', self.transport_manager),
            ('session_manager', self.session_manager),
            ('conversation_handler', self.conversation_handler),
            ('protocol_handler', self.protocol_handler),
            ('metrics_collector', self.metrics_collector),
            ('optimizer', self.optimizer)
        ]
        for name, component in components:
            if component is not None and hasattr(component, 'cleanup'):
                try:
                    await component.cleanup()
                except Exception as e:
                    error_msg = f"Failed to cleanup {name}: {str(e)}"
                    cleanup_errors.append(error_msg)
                    self.logger.error(error_msg)
        if cleanup_errors:
            raise Exception("Cleanup errors occurred:\n" + "\n".join(cleanup_errors))

    async def _monitor_server_health(self):
        """Periodically check server health and component statuses."""
        while not self.shutdown_event.is_set():
            try:
                # Update CPU and memory usage
                process = psutil.Process(self.pid)
                self.metrics["cpu_percent"] = process.cpu_percent(interval=None)
                self.metrics["memory_percent"] = process.memory_percent()

                # Check component health
                components_healthy = await self.is_healthy()

                if not components_healthy:
                    self.logger.warning("One or more server components are unhealthy.")

                self._last_health_check = datetime.now(timezone.utc)
                await asyncio.sleep(self.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)

        self.logger.info("Server health monitoring task exited.")

    async def process_message(self, message: Dict[str, Any]) -> MessageStream:
        """Process an incoming message."""
        start_time = asyncio.get_event_loop().time()
        self.metrics["total_requests"] += 1

        try:
            # Check component state
            if self.component_state != ComponentState.READY:
                yield self._create_error_response(
                    {
                        "code": ErrorCodes.SERVER_NOT_INITIALIZED.value,
                        "message": "Server not ready",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    message.get("id")
                )
                return

            if not self.is_message_valid(message):
                yield self._create_error_response(
                    {
                        "code": ErrorCodes.INVALID_REQUEST.value,
                        "message": "Invalid message format",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    message.get("id")
                )
                return

            # Add backpressure handling
            if self.metrics_collector and self.metrics["memory_percent"] > 80:
                await self._handle_backpressure()

            async for response in self.protocol_handler.handle_message(message):
                yield response

            self.metrics["successful_requests"] += 1

            elapsed = asyncio.get_event_loop().time() - start_time
            self._update_average_processing_time(elapsed)

        except Exception as e:
            self.metrics["failed_requests"] += 1
            self.logger.error(f"Message processing error: {e}")

            if isinstance(e, ProtocolError):
                error_dict = e.to_dict()
            else:
                error_dict = {
                    "code": ErrorCodes.INTERNAL_ERROR.value,
                    "message": str(e),
                    "data": {
                        "type": e.__class__.__name__,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }

            yield self._create_error_response(error_dict, message.get("id"))

    def is_message_valid(self, message: Dict[str, Any]) -> bool:
        """Validate incoming message format."""
        return (
            isinstance(message, dict)
            and "method" in message
            and isinstance(message["method"], str)
        )

    def _create_error_response(
        self,
        error: Dict[str, Any],
        message_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "error": error,
            "id": message_id
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get server status information."""
        active_sessions = (
            await self.session_manager.get_active_sessions()
            if self.session_manager else []
        )

        component_metrics = {}
        if self.conversation_handler:
            component_metrics["conversation"] = await self.conversation_handler.get_metrics()
        if self.protocol_handler and hasattr(self.protocol_handler, "get_metrics"):
            component_metrics["protocol"] = await self.protocol_handler.get_metrics()
        if self.metrics_collector:
            component_metrics["metrics_collector"] = await self.metrics_collector.get_metrics()

        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        return {
            "version": str(self.PROTOCOL_VERSION),
            "component_state": self.component_state.value,
            "uptime_seconds": uptime,
            "active_sessions": len(active_sessions),
            "component_metrics": component_metrics,
            "server_metrics": self.metrics,
            "initialization_time": self.start_time.isoformat(),
            "pid": self.pid
        }

    async def is_healthy(self) -> bool:
        """Check server health status."""
        try:
            return all([
                self.initialized,
                not self.shutdown_event.is_set(),
                self.component_state == ComponentState.READY,
                await self.session_manager.is_healthy() if self.session_manager else True,
                await self.connection_manager.is_healthy() if self.connection_manager else False,
                await self.transport_manager.is_healthy() if self.transport_manager else False,
                await self.protocol_handler.is_healthy() if hasattr(self.protocol_handler, 'is_healthy') else False,
                await self.metrics_collector.is_healthy() if self.metrics_collector else False
            ])
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return False

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Set shutdown event first
            self.shutdown_event.set()

            # Cancel health check task
            if self._health_check_task and not self._health_check_task.done():
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass

            # Cleanup components in reverse initialization order
            await self._cleanup_partial_initialization()

            self.initialized = False
            self.logger.info("Server shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during server shutdown: {e}")
            raise

    def _update_average_processing_time(self, elapsed: float):
        """Update the average processing time metric."""
        total_reqs = self.metrics["total_requests"]
        current_avg = self.metrics["average_processing_time"]
        self.metrics["average_processing_time"] = (
            (current_avg * (total_reqs - 1) + elapsed) / total_reqs
        )

    async def _handle_backpressure(self):
        """Enhanced backpressure handling with adaptive delays."""
        memory_percent = psutil.Process(self.pid).memory_percent()

        # Calculate adaptive delay based on memory pressure
        delay = min((memory_percent - 80) / 10, 5)  # Max 5 second delay
        self.logger.warning(f"Applying backpressure with {delay:.2f}s delay")

        # Notify components of backpressure
        if self.metrics_collector:
            await self.metrics_collector.record_backpressure(memory_percent)

        await asyncio.sleep(delay)

    async def _attempt_component_recovery(self, component_name: str) -> bool:
        """Attempt to recover unhealthy component."""
        try:
            component = getattr(self, component_name)
            if component and hasattr(component, 'initialize'):
                await component.initialize()
                return True
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for {component_name}: {e}")
            return False

    async def _aggregate_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics from all components."""
        aggregated = {
            "system": {
                "memory": self.metrics["memory_percent"],
                "cpu": self.metrics["cpu_percent"]
            },
            "components": {},
            "requests": {
                "total": self.metrics["total_requests"],
                "success_rate": self.metrics["successful_requests"] / max(1, self.metrics["total_requests"])
            }
        }

        for name, component in [
            ("session", self.session_manager),
            ("transport", self.transport_manager),
            ("connection", self.connection_manager),
            ("optimizer", self.optimizer)
        ]:
            if component and hasattr(component, "get_metrics"):
                aggregated["components"][name] = await component.get_metrics()

        return aggregated

    async def _get_versioned_metrics(self) -> Dict[str, Any]:
        """Get metrics with version information."""
        metrics = await self._aggregate_metrics()
        return {
            "version": MetricsVersion.to_string(),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics
        }

    async def _cleanup_resources(self):
        """Enhanced resource cleanup."""
        try:
            process = psutil.Process(self.pid)

            # Clean file handles
            for handler in process.open_files():
                try:
                    handler.close()
                except Exception as e:
                    self.logger.debug(f"Failed to close file handle: {e}")

            # Clean network connections
            for conn in process.connections():
                try:
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Failed to close connection: {e}")

            # Clean memory
            import gc
            gc.collect()

        except Exception as e:
            self.logger.error(f"Resource cleanup error: {e}")

# Export for type checking
__all__ = ['MCPServer', 'MetricsVersion']
