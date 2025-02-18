"""
Enhanced Protocol Handler Implementation

Features:
- Comprehensive message handling and validation
- Proper streaming support
- Enhanced error handling with recovery
- Complete security validation
- Resource-aware processing
"""

import asyncio
import logging
import sys
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, AsyncIterator, List, Set, Union, AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import psutil
import gc
from functools import wraps
from pydantic import ValidationError  # Import the ValidationError class

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
    OptimizationStream,
    ProcessingLevel
)
from .interfaces import (
    ServerInterface,
    OptimizerInterface,
    ProtocolInterface,
    RateLimiterInterface,
    MetricsInterface,
    ConnectionInterface
)
from .models import (
    ProtocolMessage,
    ProtocolResponse,
    ProtocolMethod,
    OptimizationRequest,
    InitializationRequest,
    InitializationResponse
)
from .utils.json_utils import dumps_with_datetime, loads_with_datetime

@dataclass
class ProtocolMetrics:
    """Track protocol-specific metrics."""
    total_messages: int = 0
    successful_messages: int = 0
    failed_messages: int = 0
    streaming_messages: int = 0
    average_processing_time: float = 0.0
    error_counts: Dict[str, int] = field(default_factory=dict)
    last_error_time: Optional[datetime] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)

class ProtocolState:
    """Track protocol state including handshake and session info."""
    def __init__(self):
        self.initialized: bool = False
        self.handshake_complete: bool = False
        self.binary_mode: bool = False
        self.session_id: Optional[str] = None
        self.client_capabilities: Dict[str, Any] = {}
        self.last_activity: datetime = datetime.now(timezone.utc)
        self.message_count = 0
        self.error_count = 0
        self.security_context: Optional[SecurityContext] = None

    def update_activity(self):
        """Update last activity timestamp and increment message count."""
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1

    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if protocol state has expired."""
        return (datetime.now(timezone.utc) - self.last_activity).total_seconds() > timeout_seconds

class ProtocolHandler(ProtocolInterface):
    """Enhanced protocol handler with comprehensive error handling and security."""

    def __init__(
        self,
        optimizer: OptimizerInterface,
        config: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Dict[str, Any]] = None,
        metrics_collector: Optional[MetricsInterface] = None
    ):
        """Initialize protocol handler with dependencies."""
        self.optimizer = optimizer
        self.config = config or {}
        self.logger = logging.getLogger("protocol-handler")
        self.dependencies = dependencies or {}
        self.metrics_collector = metrics_collector

        # Extract dependencies
        self.rate_limiter = self.dependencies.get('rate_limiter')
        self.connection_manager = self.dependencies.get('connection_manager')

        # State initialization
        self.state = ProtocolState()
        self._message_lock = asyncio.Lock()
        self._handshake_lock = asyncio.Lock()

        # Windows-specific configuration
        if sys.platform == "win32":
            self.state.binary_mode = True

        # Protocol version validation
        self.version = MCPVersion.parse(PROTOCOL_VERSION)
        self.min_version = MCPVersion.parse(MINIMAL_COMPATIBLE_VERSION)

        # Metrics tracking
        self.metrics = ProtocolMetrics()

        # Component state
        self.component_state = ComponentState.UNINITIALIZED

    async def initialize(self) -> bool:
        """Initialize protocol handler."""
        try:
            self.component_state = ComponentState.INITIALIZING

            # Verify dependencies
            if not self.optimizer:
                raise ValueError("optimizer is required")

            # Set up protocol state
            self.state.initialized = True
            self.component_state = ComponentState.READY
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def handle_message(
        self,
        message: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle incoming messages with streaming support."""
        start_time = datetime.now(timezone.utc)

        try:
            async with self._message_lock:
                # Message type validation
                try:
                    msg_type = MessageType(message.get("msg_type", ""))
                except ValueError:
                    raise ProtocolError("Invalid message type", ErrorCodes.INVALID_REQUEST)

                # Validate message format
                if not self.validate_message_format(message):
                    raise ProtocolError("Invalid message format", ErrorCodes.INVALID_REQUEST)

                # Rate limit check
                if self.rate_limiter:
                    await self._check_rate_limits(message)

                # Route message based on type
                async for response in self._process_message(message):
                    yield response

                # Update metrics
                self._update_metrics(start_time)

        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
            self.metrics.failed_messages += 1
            self.metrics.last_error_time = datetime.now(timezone.utc)
            self.metrics.error_counts[type(e).__name__] = (
                self.metrics.error_counts.get(type(e).__name__, 0) + 1
            )

            if isinstance(e, ProtocolError):
                yield self._create_error_response(e, message.get("id"))
            else:
                yield self._create_error_response(
                    ProtocolError("Internal error", ErrorCodes.INTERNAL_ERROR),
                    message.get("id")
                )

    async def _process_message(
        self,
        message: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Route and process messages based on type and method."""
        try:
            msg_type = MessageType(message.get("msg_type"))
            method = message.get("method")

            if msg_type == MessageType.REQUEST:
                async for response in self._handle_request(message):
                    yield response
            elif msg_type == MessageType.NOTIFICATION:
                async for response in self._handle_notification(message):
                    yield response
            elif msg_type == MessageType.CONTROL:
                async for response in self._handle_control_message(message):
                    yield response
            else:
                raise ProtocolError(f"Unhandled message type: {msg_type}", ErrorCodes.INVALID_REQUEST)

        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
            raise

    async def _handle_request(
        self,
        message: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle REQUEST messages."""
        method = message.get("method")

        if method == ProtocolMethod.INITIALIZE.value:
            response = await self._handle_handshake(message)
            yield self._create_response(response, message.get("id"))

        elif method == ProtocolMethod.OPTIMIZE_PROMPT.value:
            async for result in self._handle_optimize_prompt(message):
                yield result

        elif method == ProtocolMethod.SHUTDOWN.value:
            yield await self._handle_shutdown(message)

        elif method == ProtocolMethod.STATUS.value:
            yield await self._handle_status(message)

        else:
            raise ProtocolError(f"Unknown method: {method}", ErrorCodes.METHOD_NOT_FOUND)

    async def _handle_handshake(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced handshake with security validation."""
        async with self._handshake_lock:
            try:
                client_caps = message.get("params", {}).get("capabilities", {})

                # Version compatibility check
                client_version = client_caps.get("version", "2.0.0")
                version = MCPVersion.parse(client_version)
                if not version.is_compatible(MINIMAL_COMPATIBLE_VERSION):
                    raise ProtocolError(
                        f"Incompatible client version: {client_version}",
                        ErrorCodes.VERSION_MISMATCH
                    )

                # Security context validation
                security_ctx = await self._validate_security_context(
                    message.get("security_context")
                )
                if security_ctx:
                    self.state.security_context = security_ctx

                # Update state
                self.state.client_capabilities = client_caps
                self.state.handshake_complete = True
                self.state.session_id = str(uuid.uuid4())

                return {
                    "capabilities": {
                        "version": PROTOCOL_VERSION,
                        "streaming": True,
                        "binary_mode": self.state.binary_mode,
                        "security": {
                            "encryption_required": security_ctx.require_encryption
                            if security_ctx else False
                        }
                    },
                    "session": {
                        "id": self.state.session_id,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                }

            except Exception as e:
                self.logger.error(f"Handshake error: {e}")
                raise

    async def _validate_security_context(
        self,
        security_ctx: Optional[Dict[str, Any]]
    ) -> Optional[SecurityContext]:
        """Validate security context with proper error handling."""
        if not security_ctx:
            return None

        try:
            context = SecurityContext(**security_ctx)
            if context.require_encryption:
                if not self.connection_manager:
                    raise ProtocolError(
                        "Connection manager required for encryption validation",
                        ErrorCodes.INTERNAL_ERROR
                    )
                if not await self.connection_manager.is_encrypted():
                    raise ProtocolError(
                        "Encryption required",
                        ErrorCodes.UNAUTHORIZED
                    )
            return context

        except ValidationError as e:
            raise ProtocolError(
                f"Invalid security context: {e}",
                ErrorCodes.INVALID_REQUEST
            )

    async def _handle_optimize_prompt(
        self,
        message: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle optimize_prompt requests with streaming support."""
        if not self.state.handshake_complete:
            raise ProtocolError(
                "Handshake required before optimization",
                ErrorCodes.SERVER_NOT_INITIALIZED
            )

        try:
            request = OptimizationRequest(**message.get("params", {}))
            stream_enabled = request.stream

            if stream_enabled:
                self.metrics.streaming_messages += 1

            async for result in self.optimizer.optimize_stream(request.dict()):
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "optimized_prompt": result.interim_result,
                        "confidence_score": result.confidence_score,
                        "complete": result.complete,
                        "metadata": result.metadata
                    }
                }
                yield response

        except Exception as e:
            self.logger.error(f"Optimization error: {e}")
            raise

    def _create_response(self, result: Any, id_value: Optional[str] = None) -> Dict[str, Any]:
        """Create a JSON-RPC response."""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": id_value
        }

    def _create_error_response(
        self,
        error: ProtocolError,
        id_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": error.error_code,
                "message": str(error),
                "data": getattr(error, "details", None)
            },
            "id": id_value
        }

    async def _check_rate_limits(self, message: Dict[str, Any]) -> None:
        """Check message rate limits."""
        if not self.rate_limiter:
            return

        try:
            client_id = self.state.session_id or message.get("client_id")
            message_size = len(dumps_with_datetime(message))
            await self.rate_limiter.acquire(
                client_id=client_id,
                size=message_size
            )
        except Exception as e:
            raise ProtocolError(str(e), ErrorCodes.RATE_LIMIT_EXCEEDED)

    def _update_metrics(self, start_time: datetime) -> None:
        """Update protocol metrics."""
        self.metrics.total_messages += 1
        self.metrics.successful_messages += 1

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        total_msgs = self.metrics.successful_messages
        self.metrics.average_processing_time = (
            (self.metrics.average_processing_time * (total_msgs - 1) + elapsed) / total_msgs
        )

    async def is_healthy(self) -> bool:
        """Check protocol handler health."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            if not self.state.initialized:
                return False

            memory_usage = psutil.Process().memory_percent()
            if memory_usage > 90:  # Critical threshold
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self) -> None:
        """Cleanup protocol handler resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Clear state
            self.state = ProtocolState()

            # Force garbage collection
            gc.collect()

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Protocol handler cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.component_state = ComponentState.ERROR
            raise

    async def get_metrics(self) -> Dict[str, Any]:
        """Get protocol metrics."""
        return {
            "messages": {
                "total": self.metrics.total_messages,
                "successful": self.metrics.successful_messages,
                "failed": self.metrics.failed_messages,
                "streaming": self.metrics.streaming_messages
            },
            "performance": {
                "average_processing_time": self.metrics.average_processing_time
            },
            "errors": self.metrics.error_counts,
            "last_error": self.metrics.last_error_time.isoformat()
            if self.metrics.last_error_time else None,
            "state": self.component_state.value
        }

    def validate_message_format(self, message: Dict[str, Any]) -> bool:
        """Validate incoming message format."""
        try:
            # Basic structure checks
            if not isinstance(message, dict):
                return False

            # Check required fields based on message type
            try:
                msg_type = MessageType(message.get("msg_type", ""))
            except ValueError:
                return False

            if msg_type == MessageType.REQUEST:
                return self._validate_request_message(message)
            elif msg_type == MessageType.NOTIFICATION:
                return self._validate_notification_message(message)
            elif msg_type == MessageType.CONTROL:
                return self._validate_control_message(message)

            return False

        except Exception as e:
            self.logger.error(f"Message validation error: {e}")
            return False

    def _validate_request_message(self, message: Dict[str, Any]) -> bool:
        """Validate REQUEST message format."""
        required_fields = {"jsonrpc", "method", "id"}
        if not all(field in message for field in required_fields):
            return False

        if message.get("jsonrpc") != "2.0":
            return False

        # Validate method
        try:
            ProtocolMethod(message.get("method"))
        except ValueError:
            return False

        return True

    def _validate_notification_message(self, message: Dict[str, Any]) -> bool:
        """Validate NOTIFICATION message format."""
        required_fields = {"jsonrpc", "method"}
        if not all(field in message for field in required_fields):
            return False

        if message.get("jsonrpc") != "2.0":
            return False

        return True

    def _validate_control_message(self, message: Dict[str, Any]) -> bool:
        """Validate CONTROL message format."""
        required_fields = {"jsonrpc", "method", "control_type"}
        if not all(field in message for field in required_fields):
            return False

        if message.get("jsonrpc") != "2.0":
            return False

        return True

    async def _handle_notification(
        self,
        message: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle NOTIFICATION messages."""
        try:
            method = message.get("method")
            if not method:
                raise ProtocolError("Missing method in notification", ErrorCodes.INVALID_REQUEST)

            # Process notification without response
            self.logger.debug(f"Processing notification: {method}")
            self.state.update_activity()

            # No response for notifications
            yield self._create_response({"status": "notification_processed"}, None)

        except Exception as e:
            self.logger.error(f"Notification handling error: {e}")
            raise

    async def _handle_control_message(
        self,
        message: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle CONTROL messages."""
        try:
            control_type = message.get("control_type")
            if not control_type:
                raise ProtocolError("Missing control_type", ErrorCodes.INVALID_REQUEST)

            # Process control message
            response = await self._process_control(control_type, message.get("params", {}))
            yield self._create_response(response, message.get("id"))

        except Exception as e:
            self.logger.error(f"Control message handling error: {e}")
            raise

    async def _process_control(
        self,
        control_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process control message based on type."""
        if control_type == "ping":
            return {"pong": datetime.now(timezone.utc).isoformat()}
        elif control_type == "reset":
            return await self._handle_reset(params)
        else:
            raise ProtocolError(f"Unknown control type: {control_type}", ErrorCodes.INVALID_REQUEST)

    async def _handle_reset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reset control message."""
        try:
            # Reset protocol state
            self.state = ProtocolState()
            self.state.initialized = True

            # Force garbage collection
            gc.collect()

            return {
                "status": "reset_complete",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            self.logger.error(f"Reset handling error: {e}")
            raise

    async def _handle_shutdown(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shutdown request."""
        try:
            # Perform cleanup
            await self.cleanup()

            return self._create_response({
                "status": "shutdown_complete",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, message.get("id"))

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            raise

    async def _handle_status(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status request."""
        try:
            metrics = await self.get_metrics()
            return self._create_response({
                "status": "ready" if self.component_state == ComponentState.READY else "error",
                "uptime_seconds": (
                    datetime.now(timezone.utc) - self.state.last_activity
                ).total_seconds(),
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, message.get("id"))

        except Exception as e:
            self.logger.error(f"Status error: {e}")
            raise

# Export classes for type checking
__all__ = [
    'ProtocolHandler',
    'ProtocolState',
    'ProtocolMetrics'
]
