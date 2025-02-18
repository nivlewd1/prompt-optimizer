"""
Enhanced Connection Handler Implementation

Core components and base structures for connection management.
Features:
- Enhanced resource tracking and cleanup
- Proper async context handling
- Comprehensive error handling with recovery
- Windows-specific optimizations
- Cross-component integration
"""

import asyncio
import logging
import sys
import os
import json
import uuid
import time
import gc  # Import the garbage collection module
from typing import Dict, Any, Optional, AsyncIterator, List, Set, Union, DefaultDict, NamedTuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import weakref
import psutil
from contextlib import asynccontextmanager
import socket
from websockets.server import WebSocketServerProtocol

from .shared_types import (
    TransportType,
    ProtocolError,
    ErrorCodes,
    MCPVersion,
    ComponentState,
    MessageType,
    SecurityContext,
    PROTOCOL_VERSION,
    MINIMAL_COMPATIBLE_VERSION,
    MessageStream,
    RateLimitState,
    RateLimitError
)
from .interfaces import (
    ServerInterface,
    TransportInterface,
    ConversationHandlerInterface,
    RateLimiterInterface,
    MetricsInterface,
    ConnectionInterface
)

# Constants for resource management
MAX_CONNECTIONS = 1000
MEMORY_WARNING_THRESHOLD = 0.85
MEMORY_CRITICAL_THRESHOLD = 0.95
CLEANUP_INTERVAL = 300  # 5 minutes
METRICS_INTERVAL = 60   # 1 minute
WINDOWS_HANDLE_THRESHOLD = 1000

@dataclass
class ConnectionMetrics:
    """Enhanced connection metrics with Windows support."""
    total_connections: int = 0
    active_connections: int = 0
    failed_connections: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    windows_handles: int = 0
    connection_times: List[float] = field(default_factory=list)
    error_counts: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    resource_usage: Dict[str, float] = field(default_factory=dict)

    def update_windows_metrics(self):
        """Update Windows-specific metrics."""
        if sys.platform == "win32":
            try:
                process = psutil.Process()
                self.windows_handles = process.num_handles()
                self.resource_usage["handle_usage"] = self.windows_handles / WINDOWS_HANDLE_THRESHOLD
            except Exception:
                pass

@dataclass
class ConnectionState:
    """Connection state with enhanced tracking."""
    connection_id: str
    transport_type: TransportType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    component_state: ComponentState = field(default=ComponentState.UNINITIALIZED)
    security_context: Optional[SecurityContext] = None
    rate_limit_state: RateLimitState = field(default=RateLimitState.NORMAL)
    metrics: ConnectionMetrics = field(default_factory=ConnectionMetrics)
    windows_handles: int = 0
    is_active: bool = True

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        if sys.platform == "win32":
            self.update_windows_metrics()

    def update_windows_metrics(self):
        """Update Windows-specific metrics."""
        if sys.platform == "win32":
            try:
                process = psutil.Process()
                self.windows_handles = process.num_handles()
            except Exception:
                pass

    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if connection has expired."""
        return (
            not self.is_active or
            (datetime.now(timezone.utc) - self.last_activity).total_seconds() > timeout_seconds
        )

class ConnectionManager(ConnectionInterface):
    """Enhanced connection manager with resource awareness."""

    def __init__(
        self,
        config: Dict[str, Any],
        logger: logging.Logger,
        dependencies: Optional[Dict[str, Any]] = None
    ):
        """Initialize connection manager with dependencies."""
        self.config = config
        self.logger = logger
        self.dependencies = dependencies or {}

        # Extract dependencies
        self.transport_manager = self.dependencies.get('transport_manager')
        if not self.transport_manager:
            raise ValueError("transport_manager is required")

        self.protocol_handler = self.dependencies.get('protocol_handler')
        if not self.protocol_handler:
            raise ValueError("protocol_handler is required")

        self.rate_limiter = self.dependencies.get('rate_limiter')
        self.metrics_collector = self.dependencies.get('metrics_collector')

        # Connection management
        self._connections: Dict[str, ConnectionState] = {}
        self._transport_sessions: Dict[str, Set[str]] = {
            TransportType.WEBSOCKET.value: set(),
            TransportType.STDIO.value: set()
        }
        self._connection_lock = asyncio.Lock()

        # Component state
        self.component_state = ComponentState.UNINITIALIZED
        self.is_shutting_down = False

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

        # Metrics tracking
        self.metrics = ConnectionMetrics()

        # Windows specific configuration
        if sys.platform == "win32":
            self._setup_windows_manager()

    def _setup_windows_manager(self) -> None:
        """Configure Windows-specific settings."""
        if sys.platform == "win32":
            try:
                self._windows_handle_threshold = self.config.get(
                    'windows_handle_threshold',
                    WINDOWS_HANDLE_THRESHOLD
                )
                self._monitor_handles = True
            except Exception as e:
                self.logger.error(f"Windows manager setup failed: {e}")
                self._monitor_handles = False

    async def initialize(self) -> bool:
        """Initialize connection manager."""
        try:
            self.component_state = ComponentState.INITIALIZING

            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())

            self.component_state = ComponentState.READY
            self.logger.info("Connection manager initialized successfully")
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def create_connection(
        self,
        transport_type: str,
        client_id: str,
        **kwargs: Any
    ) -> Optional[str]:
        """Create new connection with resource tracking."""
        try:
            # Validate transport type
            if transport_type not in [TransportType.STDIO.value, TransportType.WEBSOCKET.value]:
                raise ValueError(f"Invalid transport type: {transport_type}")

            # Check STDIO limitation
            if (transport_type == TransportType.STDIO.value and
                len(self._transport_sessions[TransportType.STDIO.value]) > 0):
                raise ValueError("Only one STDIO connection allowed")

            # Create connection state
            connection_id = str(uuid.uuid4())
            state = ConnectionState(
                connection_id=connection_id,
                transport_type=TransportType(transport_type)
            )

            # Apply rate limiting if enabled
            if self.rate_limiter:
                await self.rate_limiter.acquire(client_id)

            async with self._connection_lock:
                # Check resource limits
                if len(self._connections) >= MAX_CONNECTIONS:
                    raise ResourceWarning("Maximum connections reached")

                # Store connection
                self._connections[connection_id] = state
                self._transport_sessions[transport_type].add(connection_id)

                # Update metrics
                self.metrics.total_connections += 1
                self.metrics.active_connections += 1

                if sys.platform == "win32":
                    self.metrics.update_windows_metrics()

            return connection_id

        except Exception as e:
            self.logger.error(f"Connection creation failed: {e}")
            self.metrics.failed_connections += 1
            if self.metrics_collector:
                await self.metrics_collector.record_error(
                    "CONNECTION_CREATION",
                    "connection_manager",
                    e
                )
            return None

    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle message from connection."""
        state = self._connections.get(connection_id)
        if not state:
            raise ValueError(f"Invalid connection: {connection_id}")

        try:
            # Update activity
            state.update_activity()

            # Rate limiting
            if self.rate_limiter:
                client_id = message.get("client_id", connection_id)
                message_size = len(json.dumps(message))
                await self.rate_limiter.acquire(
                    client_id=client_id,
                    size=message_size
                )

            # Process message
            async for response in self.protocol_handler.handle_message(message):
                yield response

            # Update metrics
            state.metrics.bytes_received += len(str(message))

        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
            state.metrics.error_counts["message_handling"] += 1
            if self.metrics_collector:
                await self.metrics_collector.record_error(
                    "MESSAGE_HANDLING",
                    "connection_manager",
                    e
                )
            raise

    async def close_connection(self, connection_id: str) -> None:
        """Close connection and cleanup resources."""
        async with self._connection_lock:
            if connection_id in self._connections:
                state = self._connections[connection_id]
                state.is_active = False

                # Remove from transport tracking
                self._transport_sessions[state.transport_type.value].discard(connection_id)

                # Cleanup connection
                await self._cleanup_connection(connection_id)

                # Update metrics
                self.metrics.active_connections -= 1

    async def _cleanup_connection(self, connection_id: str) -> None:
        """Cleanup connection resources."""
        try:
            if connection_id in self._connections:
                state = self._connections.pop(connection_id)

                # Windows-specific cleanup
                if sys.platform == "win32" and state.windows_handles > 0:
                    process = psutil.Process()
                    for handle in process.open_files()[:state.windows_handles]:
                        try:
                            handle.close()
                        except Exception as e:
                            self.logger.error(f"Handle cleanup error: {e}")

        except Exception as e:
            self.logger.error(f"Connection cleanup error: {e}")
            raise

    async def _monitor_loop(self) -> None:
        """Monitor connections and system resources."""
        while not self.is_shutting_down:
            try:
                await asyncio.sleep(METRICS_INTERVAL)

                async with self._connection_lock:
                    # Check connections
                    for conn_id, state in list(self._connections.items()):
                        if state.is_expired(self.config.get('connection_timeout', 1800)):
                            await self.close_connection(conn_id)

                    # Check resource usage
                    if sys.platform == "win32" and self._monitor_handles:
                        process = psutil.Process()
                        if process.num_handles() > self._windows_handle_threshold:
                            await self._handle_resource_pressure()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                await asyncio.sleep(1)

    async def _handle_resource_pressure(self) -> None:
        """Handle high resource usage."""
        self.logger.warning("High resource usage detected")
        try:
            # Close oldest connections
            sorted_connections = sorted(
                self._connections.items(),
                key=lambda x: x[1].last_activity
            )

            # Close 10% of connections
            to_close = len(sorted_connections) // 10
            for conn_id, _ in sorted_connections[:to_close]:
                await self.close_connection(conn_id)

            # Force garbage collection
            gc.collect()

        except Exception as e:
            self.logger.error(f"Resource pressure handling failed: {e}")

    async def _metrics_loop(self) -> None:
        """Collect and update metrics."""
        while not self.is_shutting_down:
            try:
                await asyncio.sleep(METRICS_INTERVAL)

                metrics = await self.get_metrics()
                if self.metrics_collector:
                    await self.metrics_collector.collect_metrics(metrics)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics error: {e}")
                await asyncio.sleep(1)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive connection metrics."""
        return {
            "connections": {
                "total": self.metrics.total_connections,
                "active": self.metrics.active_connections,
                "failed": self.metrics.failed_connections
            },
            "transport_sessions": {
                t_type: len(sessions)
                for t_type, sessions in self._transport_sessions.items()
            },
            "resources": {
                "windows_handles": self.metrics.windows_handles
                if sys.platform == "win32" else None,
                "memory_usage": psutil.Process().memory_percent()
            },
            "errors": dict(self.metrics.error_counts),
            "component_state": self.component_state.value
        }

    async def is_healthy(self) -> bool:
        """Check connection manager health."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            # Check background tasks
            if any(
                task and task.done()
                for task in [self._cleanup_task, self._monitor_task, self._metrics_task]
            ):
                return False

            # Check resource usage
            if sys.platform == "win32" and self._monitor_handles:
                process = psutil.Process()
                if process.num_handles() > self._windows_handle_threshold:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self) -> None:
        """Cleanup connection manager resources."""
        self.logger.info("Starting connection manager cleanup")
        self.is_shutting_down = True

        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Cancel background tasks
            for task in [self._cleanup_task, self._monitor_task, self._metrics_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            # Close all connections
            async with self._connection_lock:
                for conn_id in list(self._connections.keys()):
                    await self.close_connection(conn_id)

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Connection manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.component_state = ComponentState.ERROR
            raise

    @asynccontextmanager
    async def connection_context(
        self,
        connection_id: str,
        auto_close: bool = True
    ):
        """Context manager for connection operations."""
        try:
            if connection_id not in self._connections:
                raise ValueError(f"Invalid connection: {connection_id}")
            yield self._connections[connection_id]
        finally:
            if auto_close:
                await self.close_connection(connection_id)

    def is_encrypted(self) -> bool:
        """Check if connection manager uses encrypted transport."""
        # Check if transport manager supports encryption
        return (
            hasattr(self.transport_manager, 'is_encrypted') and
            self.transport_manager.is_encrypted()
        )

    async def verify_connection(self, connection_id: str) -> bool:
        """Verify connection is valid and active."""
        state = self._connections.get(connection_id)
        if not state:
            return False
        return state.is_active and not state.is_expired(
            self.config.get('connection_timeout', 1800)
        )

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired connections."""
        while not self.is_shutting_down:
            try:
                await asyncio.sleep(CLEANUP_INTERVAL)

                async with self._connection_lock:
                    # Get expired connections
                    expired = [
                        conn_id for conn_id, state in self._connections.items()
                        if state.is_expired(self.config.get('connection_timeout', 1800))
                    ]

                    # Cleanup expired connections
                    for conn_id in expired:
                        await self.close_connection(conn_id)

                    # Update metrics
                    self.metrics.active_connections = len(self._connections)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(1)

    async def _check_resource_limits(self) -> None:
        """Check and handle resource limits."""
        try:
            process = psutil.Process()

            # Check memory usage
            memory_percent = process.memory_percent()
            if memory_percent > MEMORY_CRITICAL_THRESHOLD:
                self.logger.error("Critical memory usage detected")
                await self._handle_critical_memory()
            elif memory_percent > MEMORY_WARNING_THRESHOLD:
                self.logger.warning("High memory usage detected")
                await self._handle_high_memory()

            # Check Windows handles
            if sys.platform == "win32" and self._monitor_handles:
                handles = process.num_handles()
                if handles > self._windows_handle_threshold:
                    self.logger.warning(f"High handle count: {handles}")
                    await self._handle_resource_pressure()

        except Exception as e:
            self.logger.error(f"Resource check error: {e}")

    async def _handle_critical_memory(self) -> None:
        """Handle critical memory usage situation."""
        try:
            # Force immediate cleanup
            async with self._connection_lock:
                # Close all non-essential connections
                for conn_id, state in list(self._connections.items()):
                    if state.transport_type != TransportType.STDIO:
                        await self.close_connection(conn_id)

            # Force garbage collection
            gc.collect()

        except Exception as e:
            self.logger.error(f"Critical memory handling error: {e}")

    async def _handle_high_memory(self) -> None:
        """Handle high memory usage situation."""
        try:
            # Close oldest connections first
            async with self._connection_lock:
                sorted_connections = sorted(
                    self._connections.items(),
                    key=lambda x: x[1].last_activity
                )

                # Close up to 25% of connections
                to_close = len(sorted_connections) // 4
                for conn_id, _ in sorted_connections[:to_close]:
                    await self.close_connection(conn_id)

        except Exception as e:
            self.logger.error(f"High memory handling error: {e}")

    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return len(self._connections)

    @property
    def connection_limit_reached(self) -> bool:
        """Check if connection limit is reached."""
        return len(self._connections) >= MAX_CONNECTIONS

# Export for type checking
__all__ = ['ConnectionManager', 'ConnectionState', 'ConnectionMetrics']
