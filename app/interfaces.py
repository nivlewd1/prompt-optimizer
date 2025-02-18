from typing import Dict, List, Any, Protocol, runtime_checkable, Optional, AsyncIterator, Tuple, Union, Callable
from enum import Enum
from datetime import datetime
from abc import abstractmethod
from .shared_types import OptimizationStream, PatternCategory, StrategyContext, RateLimitMetrics, RateLimitState, RateLimitConfig, SecurityContext, MessageStream

# Define ComponentState for state management
class ComponentState(Enum):
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"

# Base Component Interface
@runtime_checkable
class ComponentInterface(Protocol):
    """Base interface for all components."""
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the component."""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup component resources."""
        ...

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the component is healthy."""
        ...

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics."""
        ...

    @abstractmethod
    async def get_component_state(self) -> ComponentState:
        """Get the current state of the component."""
        ...

# Metrics Interface
@runtime_checkable
class MetricsInterface(Protocol):
    """Interface for metrics collection."""
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics."""
        ...

    @abstractmethod
    async def reset_metrics(self) -> None:
        """Reset metrics."""
        ...

    @abstractmethod
    async def validate_metrics(self) -> List[str]:
        """Validate collected metrics."""
        ...

    @abstractmethod
    async def get_metrics_context(self) -> Dict[str, Any]:
        """Get metrics collection context."""
        ...

# Server Interface
@runtime_checkable
class ServerInterface(ComponentInterface, Protocol):
    """Interface defining required server methods."""
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message."""
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the server."""
        ...

# Initializer Interface
@runtime_checkable
class InitializerInterface(Protocol):
    """Interface for server initialization and component creation."""
    @classmethod
    @abstractmethod
    async def create_server(
        cls,
        config: Dict[str, Any],
        logger: Any
    ) -> Tuple['OptimizerInterface', 'ProtocolInterface', Dict[str, Any]]:
        """Create and initialize server components."""
        ...

    @staticmethod
    @abstractmethod
    async def validate_config(config: Dict[str, Any], logger: Any) -> List[str]:
        """Validate server configuration."""
        ...

# Optimizer Interface
@runtime_checkable
class OptimizerInterface(ComponentInterface, Protocol):
    """Interface for prompt optimization."""
    @abstractmethod
    async def optimize_stream(
        self,
        request: Dict[str, Any]
    ) -> AsyncIterator[OptimizationStream]:
        """Optimize prompt with streaming results."""
        ...

# Connection Interface
@runtime_checkable
class ConnectionInterface(ComponentInterface, Protocol):
    """Interface for connection handling."""
    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]) -> None:
        """Handle an incoming message."""
        ...

    @abstractmethod
    async def create_connection(
        self,
        transport_type: str,
        session_id: str,
        client_type: str = "generic",
        **kwargs
    ) -> Any:
        """Create a new connection."""
        ...

# Connection Handler Interface
@runtime_checkable
class ConnectionHandlerInterface(ComponentInterface, Protocol):
    """Interface for connection handler management."""
    @abstractmethod
    async def transition_to(self, new_state: ComponentState) -> bool:
        """Transition to new component state."""
        ...

    @abstractmethod
    async def validate_handler(self) -> bool:
        """Validate handler configuration and state."""
        ...

# Transport Handler Interface
@runtime_checkable
class TransportHandlerInterface(ConnectionHandlerInterface, Protocol):
    """Interface for transport handlers."""
    @abstractmethod
    async def handle_transport_error(self, error: Exception) -> None:
        """Handle transport-specific errors."""
        ...

    @abstractmethod
    async def handle_transport_backpressure(self) -> None:
        """Handle transport-specific backpressure."""
        ...

    @abstractmethod
    async def validate_transport_message(
        self,
        message: Dict[str, Any]
    ) -> bool:
        """Validate transport-specific message."""
        ...

# Transport Interface
@runtime_checkable
class TransportInterface(ComponentInterface, Protocol):
    """Enhanced transport interface with streaming and security."""
    @abstractmethod
    async def create_secure_transport(
        self,
        transport_type: str,
        ssl_config: Optional[Dict[str, Any]] = None
    ) -> 'TransportInterface':
        pass

    @abstractmethod
    async def handle_transport_message(
        self,
        transport_type: str,
        instance_id: str,
        message: Dict[str, Any],
        security_context: SecurityContext
    ) -> MessageStream:
        pass

    @abstractmethod
    async def handle_message(
        self,
        transport_type: str,
        instance_id: str,
        message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle transport message."""
        ...

    @abstractmethod
    async def verify_transport_instance(
        self,
        transport_type: str,
        instance_id: str
    ) -> bool:
        """Verify transport instance."""
        ...

    @abstractmethod
    async def validate_transport_config(
        self,
        transport_type: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """Validate transport configuration."""
        ...

# Session Interface
@runtime_checkable
class SessionInterface(ComponentInterface, Protocol):
    """Interface for session management."""
    @abstractmethod
    async def create_session(
        self,
        client_id: str,
        transport_type: str,
        transport_instance_id: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Create a new session."""
        ...

    @abstractmethod
    async def get_session(
        self,
        session_id: str,
        transport_instance_id: Optional[str] = None
    ) -> Optional[Any]:
        """Get existing session."""
        ...

    @abstractmethod
    async def validate_session_message(
        self,
        session_id: str,
        message: Dict[str, Any],
        transport_instance_id: Optional[str] = None
    ) -> bool:
        """Validate session message."""
        ...

    @abstractmethod
    async def remove_session(self, session_id: str) -> None:
        """Remove an existing session."""
        ...

# Config Interface
@runtime_checkable
class ConfigInterface(ComponentInterface, Protocol):
    """Interface for configuration management."""
    @abstractmethod
    async def get_component_config(self, component: str) -> Dict[str, Any]:
        """Get component configuration."""
        ...

    @abstractmethod
    async def update_component_config(
        self,
        component: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update component configuration."""
        ...

    @abstractmethod
    async def validate_configuration(self) -> List[str]:
        """Validate entire configuration."""
        ...

    @abstractmethod
    async def reload_configuration(self) -> None:
        """Reload configuration from sources."""
        ...

# Protocol Interface
@runtime_checkable
class ProtocolInterface(ComponentInterface, Protocol):
    """Interface for protocol handling."""
    @abstractmethod
    async def handle_message(
        self,
        message: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle protocol message."""
        ...

    @abstractmethod
    def validate_message_format(self, message: Dict[str, Any]) -> bool:
        """Validate message format."""
        ...

# Rate Limiter Interface
@runtime_checkable
class RateLimiterInterface(ComponentInterface, Protocol):
    """Interface for rate limiting."""
    @abstractmethod
    async def acquire(
        self,
        client_id: str,
        size: int = 0,
        wait: bool = True,
        timeout: Optional[float] = None
    ) -> bool:
        """Acquire rate limit tokens."""
        ...

    @abstractmethod
    async def get_metrics(self, client_id: Optional[str] = None) -> Union[RateLimitMetrics, Dict[str, RateLimitMetrics]]:
        """Get rate limiter metrics."""
        ...

    @abstractmethod
    async def get_state(self, client_id: str) -> RateLimitState:
        """Get rate limiter current state for a client."""
        ...

    @abstractmethod
    async def set_rule(self, client_id: str, rule: RateLimitConfig) -> None:
        """Dynamically update a client rate limit rule."""
        ...

# Validation Interface
@runtime_checkable
class ValidationInterface(ComponentInterface, Protocol):
    """Interface for configuration validation."""
    @abstractmethod
    async def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration."""
        ...

    @abstractmethod
    async def validate_component(
        self,
        component: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """Validate component configuration."""
        ...

# Resource Interface
@runtime_checkable
class ResourceInterface(ComponentInterface, Protocol):
    """Interface for resource management."""
    @abstractmethod
    async def allocate_resources(
        self,
        resource_id: str,
        resources: Dict[str, int]
    ) -> bool:
        """Allocate resources."""
        ...

    @abstractmethod
    async def release_resources(self, resource_id: str) -> None:
        """Release resources."""
        ...

    @abstractmethod
    async def update_usage(
        self,
        resource_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """Update resource usage."""
        ...

# Conversation Handler Interface
@runtime_checkable
class ConversationHandlerInterface(ComponentInterface, Protocol):
    """Interface for conversation handling and optimization."""
    @abstractmethod
    async def process_message(
        self,
        message: Dict[str, Any],
        conversation_id: str
    ) -> AsyncIterator[OptimizationStream]:
        """Process and optimize message in real-time."""
        ...

    @abstractmethod
    async def cleanup_conversation(self, conversation_id: str) -> None:
        """Cleanup conversation resources."""
        ...

# Pattern Interface
@runtime_checkable
class PatternInterface(ComponentInterface, Protocol):
    """Interface for pattern-based optimization."""
    @abstractmethod
    async def apply_pattern_stream(
        self,
        prompt: str,
        pattern_type: PatternCategory,
        context: Optional[StrategyContext] = None
    ) -> AsyncIterator[OptimizationStream]:
        """Apply pattern with streaming results."""
        ...

# Strategy Interface
@runtime_checkable
class StrategyInterface(ComponentInterface, Protocol):
    """Interface for optimization strategies."""
    @abstractmethod
    async def optimize_prompt_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute optimization strategy with streaming results."""
        ...

# Resource Management Interface
@runtime_checkable
class ResourceManagementInterface(Protocol):
    """Interface for resource management."""
    @abstractmethod
    async def register_resource(
        self,
        resource_id: str,
        cleanup_handler: Callable[[], None],
        priority: int
    ) -> None:
        pass

    @abstractmethod
    async def cleanup_resources(self, priority: Optional[int] = None) -> None:
        pass

# Security Context Interface
@runtime_checkable
class SecurityContextInterface(Protocol):
    """Interface for security context management."""
    @abstractmethod
    async def create_context(
        self,
        client_id: str,
        session_id: str,
        auth_token: str,
        ip_address: str
    ) -> SecurityContext:
        pass

    @abstractmethod
    async def validate_context(self, context: SecurityContext) -> bool:
        pass

# Stream Control Interface
@runtime_checkable
class StreamControlInterface(Protocol):
    """Interface for stream control and backpressure."""
    @abstractmethod
    async def apply_backpressure(self) -> None:
        pass

    @abstractmethod
    async def release_backpressure(self) -> None:
        pass

# Audit Log Interface
@runtime_checkable
class AuditLogInterface(Protocol):
    """Interface for security audit logging."""
    @abstractmethod
    async def log_security_event(
        self,
        event_type: str,
        context: SecurityContext,
        details: Dict[str, Any]
    ) -> None:
        pass
