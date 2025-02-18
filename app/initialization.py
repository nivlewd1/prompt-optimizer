"""
Enhanced Server Initialization Implementation

Features:
- Comprehensive component lifecycle management
- Robust dependency resolution
- Enhanced resource tracking
- Proper interface validation
- Complete error handling
"""

from typing import (
    Dict, List, Any, Optional, Tuple, Callable, Set, TypeVar, Awaitable,
    TYPE_CHECKING
)
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import sys
from abc import ABC, abstractmethod  # Not used in this file, but good practice to keep.
from functools import wraps
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from collections import defaultdict, DefaultDict
import psutil
import gc

from .shared_types import (
    MCPVersion,
    ProtocolError,
    ErrorCodes,
    ProcessingLevel,
    ValidationLevel,
    TransportConfig,  # Used in validate_config
    ServerConfig,    # Not currently used but good to keep for future use.
    DSPyConfig,
    TransportType,
    ComponentState,
    OptimizerConfig  # This was missing!  It's used in _create_component
)
from .prompt_optimizer import EnhancedPromptOptimizer
from .protocol_handler import ProtocolHandler
from .interfaces import (
    ServerInterface,
    ConnectionInterface,
    TransportInterface,
    InitializerInterface,  # This was missing! It's the base class.
    OptimizerInterface,
    ProtocolInterface,
    SessionInterface,
    ConversationHandlerInterface,
    RateLimiterInterface,
    ValidationInterface # Added for ConfigManager
)
from .models import ServerStatus, ClientCapabilities # Not used, but good to keep
from .conversation_handler import ConversationHandler
from .transport_manager import TransportManager
from .config_manager import ConfigManager, ConfigurationError, ValidationError
from .rate_limiter import AdaptiveRateLimiter

if TYPE_CHECKING:
    from .connection import ConnectionManager
    from .session_manager import SessionManager

# Type variable for generic component types
T = TypeVar('T')

class ComponentError(Exception):
    """Base exception for component-related errors."""
    pass

class InitializationError(ComponentError):
    """Raised when component initialization fails."""
    pass

class ResourceError(ComponentError):
    """Raised when resource management fails."""
    pass

@dataclass
class ComponentDependency:
    """Tracks component dependencies and initialization order."""
    name: str
    interface: type
    dependencies: Set[str] = field(default_factory=set)  # Initialize with default factory
    is_optional: bool = False
    instance: Any = None
    priority: int = 0  # Add priority for initialization order
    validation_errors: List[str] = field(default_factory=list)
    initialization_attempts: int = 0
    retry_delay: float = 1.0

    def __post_init__(self):  # No need to check for None, already a set.
        self.dependencies = self.dependencies or set()

    def validate_instance(self) -> bool:
        """Validate that instance implements required interface."""
        if not self.instance and not self.is_optional:
            raise InitializationError(f"Required component {self.name} not provided")
        if self.instance and not isinstance(self.instance, self.interface):
            raise InitializationError(
                f"Component {self.name} must implement {self.interface.__name__}"
            )
        return True

class ValidationChain:
    """Enhanced validation chain for component initialization."""
    async def validate_component(
        self,
        component: Any,
        requirements: Dict[str, Any]
    ) -> List[str]:
        issues = []
        # Check interface requirements
        for method_name in requirements.get('required_methods', []):
            if not hasattr(component, method_name):
                issues.append(f"Missing required method: {method_name}")

        # Check configuration
        if hasattr(component, 'config'):
            config_issues = await self.validate_config(component.config, requirements)
            issues.extend(config_issues)

        return issues

    async def validate_config(
        self,
        config: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[str]:
        issues = []
        # Validate required sections
        required_sections = requirements.get('required_sections', [])
        missing = required_sections - set(config.keys())
        if missing:
            issues.append(f"Missing required configuration sections: {missing}")

        # Validate specific config values
        for key, value_type in requirements.get('config_types', {}).items():
            if key in config and not isinstance(config[key], value_type):
                issues.append(f"Invalid type for {key}: expected {value_type.__name__}")

        return issues

    async def validate_dependencies(
        self,
        dependencies: Dict[str, ComponentDependency]
    ) -> bool:
        # Check circular dependencies
        visited: Set[str] = set()
        temp: Set[str] = set()

        async def visit(name: str, path: List[str] = None):
            path = path or []
            if name in temp:
                cycle = " -> ".join(path + [name])
                raise InitializationError(
                    f"Circular dependency detected: {cycle}"
                )
            if name in visited:
                return

            temp.add(name)
            path.append(name)

            dep = dependencies.get(name)
            if dep:
                for d in dep.dependencies:
                    await visit(d, path.copy())

            temp.remove(name)
            visited.add(name)

        for name in dependencies:
            if name not in visited:
                await visit(name)

        return True

class InitializationResourceManager:
    """Manage resources during initialization."""

    def __init__(self, memory_threshold: int):
        self.memory_threshold = memory_threshold
        self.resource_usage: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
        # Added missing lock and initialized components attributes
        self._lock = asyncio.Lock()
        self._initialized_components: List[str] = []
        self._components: Dict[str, Any] = {}

    async def track_resources(self, component: str) -> None:
        process = psutil.Process()
        memory_usage = process.memory_info().rss
        cpu_usage = process.cpu_percent()

        self.resource_usage[component]['memory'] = memory_usage
        self.resource_usage[component]['cpu'] = cpu_usage

        if memory_usage > self.memory_threshold:
            await self._handle_memory_pressure(component)

    async def _handle_memory_pressure(self, component: str) -> None:
        """Handle high memory usage with gradual resource release."""
        self.logger.warning(f"High memory usage detected for component: {component}")
        try:
            # Suggest garbage collection
            gc.collect()
            self.logger.info(f"Garbage collection suggested for component: {component}")

            # Reduce cache sizes if the component has a cache
            comp_instance = self._components.get(component)
            if comp_instance and hasattr(comp_instance, 'reduce_cache'):
                await comp_instance.reduce_cache()
                self.logger.info(f"Reduced cache size for component: {component}")

            # Implement more aggressive memory reduction strategies if needed
            # This could involve shedding less critical tasks or connections

        except Exception as e:
            self.logger.error(f"Failed to handle memory pressure for component: {component}. Error: {e}")

    async def cleanup_resources(self, failed_components: Set[str]) -> None:
        """
        Cleanup resources with proper sequencing.

        Args:
            failed_components: Set of component names that failed initialization
        """
        cleanup_errors = []
        cleanup_order = []

        try:
            # Determine cleanup order (reverse of initialization order)
            async with self._lock:
                for component in reversed(self._initialized_components):
                    if component in failed_components:
                        cleanup_order.append(component)

            # Cleanup each component in order
            for component_name in cleanup_order:
                try:
                    component = self._components.get(component_name)
                    if component and hasattr(component, 'cleanup'):
                        await component.cleanup()

                    # Release system resources
                    if component_name in self.resource_usage:
                        memory_used = self.resource_usage[component_name].get('memory', 0)
                        handles_used = self.resource_usage[component_name].get('handles', 0)

                        # Force garbage collection if significant memory was used
                        if memory_used > 100 * 1024 * 1024:  # 100MB
                            gc.collect()

                        # Close handles on Windows
                        if sys.platform == 'win32' and handles_used > 0:
                            process = psutil.Process()
                            try:
                                for handle in process.open_files()[:handles_used]:
                                    handle.close()
                            except Exception as e:
                                cleanup_errors.append(f"Failed to close handles for {component_name}: {e}")

                except Exception as e:
                    cleanup_errors.append(f"Failed to cleanup {component_name}: {e}")

            if cleanup_errors:
                raise ResourceError(
                    f"Resource cleanup errors occurred:\n" + "\n".join(cleanup_errors)
                )

        except Exception as e:
            self.logger.error(f"Fatal error during resource cleanup: {e}")
            raise

class InitializationStateTracker:
    """Track initialization state of components."""
    def __init__(self):
        self.states: Dict[str, ComponentState] = {}
        self.transition_history: List[Dict[str, Any]] = []
        self.failed_attempts: DefaultDict[str, int] = defaultdict(int)
        self.metrics = InitializationMetrics()

    def track_state_transition(self, component: str, new_state: ComponentState) -> None:
        if component in self.states and self.states[component] != new_state:
            self.transition_history.append({
                "component": component,
                "from_state": self.states[component],
                "to_state": new_state,
                "timestamp": datetime.now().isoformat()
            })
        self.states[component] = new_state

    def record_failed_attempt(self, component: str) -> None:
        self.failed_attempts[component] += 1

class InitializationErrorHandler:
    """Handle initialization errors with recovery."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Added to fix the missing attribute error in the rollback
        self._components: Dict[str, Any] = {}
        self.resource_usage: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.metrics: InitializationMetrics = InitializationMetrics()

    async def handle_error(
        self,
        component: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> bool:
        if isinstance(error, InitializationError):
            return await self._handle_init_error(component, error)
        elif isinstance(error, ResourceError):
            return await self._handle_resource_error(component, error)
        return False

    async def _handle_init_error(self, component: str, error: InitializationError) -> bool:
        # Implement initialization error handling
        logging.error(f"Initialization error for component {component}: {error}")
        # Add logic to handle initialization error
        return True

    async def _handle_resource_error(self, component: str, error: ResourceError) -> bool:
        # Implement resource error handling
        logging.error(f"Resource error for component {component}: {error}")
        # Add logic to handle resource error
        return True

    async def rollback_component(
        self,
        component: str,
        error: Exception
    ) -> None:
        """
        Roll back a component to its previous state after failure.

        Args:
            component: Name of the component to roll back
            error: The error that triggered the rollback
        """
        try:
            # Get component instance and state
            component_instance = self._components.get(component)
            if not component_instance:
                return

            # Store current state for potential recovery
            previous_state = {
                'state': getattr(component_instance, 'state', None),
                'config': getattr(component_instance, 'config', {}).copy(),
                'resources': self.resource_usage.get(component, {}).copy()
            }

            # Perform rollback steps
            try:
                # 1. Stop any active operations
                if hasattr(component_instance, 'stop'):
                    await component_instance.stop()

                # 2. Release acquired resources
                await self.cleanup_resources({component})

                # 3. Reset to initial state
                if hasattr(component_instance, 'reset'):
                    await component_instance.reset()

                # 4. Restore previous configuration
                if hasattr(component_instance, 'config'):
                    component_instance.config = previous_state['config']

                # 5. Record rollback in metrics
                self.metrics.record_rollback(component, str(error))

                self.logger.info(f"Successfully rolled back component: {component}")

            except Exception as rollback_error:
                # If rollback fails, we need to handle it gracefully
                self.logger.error(
                    f"Rollback failed for {component}. "
                    f"Original error: {error}. "
                    f"Rollback error: {rollback_error}"
                )
                raise ResourceError(
                    f"Failed to rollback component {component}"
                ) from rollback_error

        except Exception as e:
            self.logger.error(f"Fatal error during component rollback: {e}")
            raise

@dataclass
class InitializationMetrics:
    """Track initialization metrics."""
    start_time: datetime = field(default_factory=datetime.now)
    component_times: Dict[str, float] = field(default_factory=dict)
    error_counts: DefaultDict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    resource_usage: Dict[str, float] = field(default_factory=dict)
    validation_failures: List[str] = field(default_factory=list)
    error_details: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: defaultdict(list))

    def record_rollback(self, component: str, error: str) -> None:
        self.error_counts[component] += 1
        self.validation_failures.append(f"Rollback for {component}: {error}")
        self.error_details[component].append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

class ComponentRegistry:
    """Manages component registration and dependency tracking."""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._dependencies: Dict[str, ComponentDependency] = {}
        self._initialized: Set[str] = set()
        self._lock = asyncio.Lock()
        self.resource_manager = InitializationResourceManager(memory_threshold=500 * 1024 * 1024)  # 500MB
        self.state_tracker = InitializationStateTracker()
        self.error_handler = InitializationErrorHandler()
        self.logger = logging.getLogger(__name__)

    async def register(
        self,
        name: str,
        component: Any,
        interface_type: type,
        validate: bool = True
    ) -> None:
        """Register a component with validation."""
        async with self._lock:
            if validate and not isinstance(component, interface_type):
                raise TypeError(
                    f"Component {name} must implement {interface_type.__name__}"
                )
            if name in self._components:
                raise ValueError(f"Component {name} already registered")

            self._components[name] = component
            # Also set in the error handler for rollbacks
            self.error_handler._components[name] = component

    async def get(self, name: str) -> Optional[Any]:
        """Get a registered component."""
        async with self._lock:
            return self._components.get(name)

    def add_dependency(self, dependency: ComponentDependency) -> None:
        """Add a component dependency."""
        self._dependencies[dependency.name] = dependency

    async def resolve_dependencies(self) -> List[str]:
        """Resolve initialization order based on dependencies."""
        async with self._lock:
            try:
                visited: Set[str] = set()
                temp: Set[str] = set()
                order: List[str] = []

                async def visit(name: str, path: List[str] = None):
                    path = path or []
                    if name in temp:
                        cycle = " -> ".join(path + [name])
                        raise InitializationError(
                            f"Circular dependency detected: {cycle}"
                        )
                    if name in visited:
                        return

                    temp.add(name)
                    path.append(name)

                    dep = self._dependencies.get(name)
                    if dep:
                        for d in dep.dependencies:
                            await visit(d, path.copy())

                    temp.remove(name)
                    visited.add(name)
                    order.append(name)

                for name in self._dependencies:
                    if name not in visited:
                        await visit(name)

                return order

            except Exception as e:
                raise InitializationError(f"Dependency resolution failed: {str(e)}")

    async def cleanup(self) -> None:
        """Cleanup all registered components."""
        async with self._lock:
            cleanup_errors = []
            for name, component in reversed(list(self._components.items())):
                try:
                    if hasattr(component, 'cleanup'):
                        await component.cleanup()
                except Exception as e:
                    cleanup_errors.append(f"{name}: {str(e)}")

            if cleanup_errors:
                raise InitializationError(
                    "Cleanup errors occurred:\n" + "\n".join(cleanup_errors)
                )

    async def validate_component_health(self, component: str) -> bool:
        """Validate the health of a component."""
        component_instance = self._components.get(component)
        if not component_instance:
            return False

        # Check if the component has a health check method
        if hasattr(component_instance, 'is_healthy') and callable(getattr(component_instance, 'is_healthy')):
            is_healthy = await component_instance.is_healthy()
            if not is_healthy:
                self.logger.warning(f"Component {component} reported unhealthy.")
            return is_healthy

        # Default to True if no health check method is available
        return True

class ServerInitializer(InitializerInterface):
    """Handles server component initialization and capability negotiation."""

    VERSION = MCPVersion.parse("2.0.0")

    @classmethod
    async def create_server(
        cls,
        config: Dict[str, Any],
        logger: logging.Logger
    ) -> Tuple[ServerInterface, Dict[str, Any]]:
        """Create and initialize server components."""
        try:
            # Initialize component registry
            registry = ComponentRegistry()

            # Register component dependencies in correct order
            registry.add_dependency(ComponentDependency(
                name="rate_limiter",
                interface=RateLimiterInterface,
                dependencies=set()
            ))

            registry.add_dependency(ComponentDependency(
                name="optimizer",
                interface=OptimizerInterface,
                dependencies={"rate_limiter"}
            ))

            registry.add_dependency(ComponentDependency(
                name="conversation_handler",
                interface=ConversationHandlerInterface,
                dependencies={"optimizer"},
                is_optional=True
            ))

            registry.add_dependency(ComponentDependency(
                name="protocol_handler",
                interface=ProtocolInterface,
                dependencies={"optimizer", "rate_limiter"}
            ))

            registry.add_dependency(ComponentDependency(
                name="transport_manager",
                interface=TransportInterface,
                dependencies={"conversation_handler", "protocol_handler"}
            ))

            registry.add_dependency(ComponentDependency(
                name="connection_manager",
                interface=ConnectionInterface,
                dependencies={"transport_manager", "protocol_handler"}
            ))

            registry.add_dependency(ComponentDependency(
                name="session_manager",
                interface=SessionInterface,
                dependencies={"protocol_handler", "connection_manager"}
            ))

            # Create components in resolved order
            initialization_order = await registry.resolve_dependencies()

            for component_name in initialization_order:
                component = await cls._create_component(
                    component_name,
                    config,
                    logger,
                    registry
                )
                if component:
                    await registry.register(
                        component_name,
                        component,
                        registry._dependencies[component_name].interface
                    )
                    if hasattr(component, 'initialize'):
                        if not await component.initialize():
                            raise InitializationError(
                                f"Failed to initialize {component_name}"
                            )

            # Create server instance
            server = await cls._create_server_instance(config, logger, registry)

            # Initialize capabilities
            capabilities = {
                "version": str(cls.VERSION),
                "methods": [
                    "initialize",
                    "optimize_prompt",
                    "shutdown",
                    "status"
                ],
                "features": {
                    "rate_limiting": True,
                    "streaming": True,
                    "conversation_optimization": bool(
                        await registry.get("conversation_handler")
                    )
                }
            }

            return server, capabilities

        except Exception as e:
            logger.error(f"Server initialization failed: {str(e)}")
            await registry.cleanup()
            raise ProtocolError(
                "Initialization failed",
                ErrorCodes.SERVER_NOT_INITIALIZED,
                {"error": str(e)}
            )

    @classmethod
    async def _create_component(
        cls,
        component_name: str,
        config: Dict[str, Any],
        logger: logging.Logger,
        registry: ComponentRegistry
    ) -> Any:
        """Create a specific component with lifecycle management."""
        try:
            if component_name == "rate_limiter":
                return AdaptiveRateLimiter(config.get('rate_limiter', {}))

            elif component_name == "optimizer":
                optimizer_config = config.get('optimizer', {})
                rate_limiter = await registry.get("rate_limiter")
                return EnhancedPromptOptimizer(config=optimizer_config, rate_limiter=rate_limiter)

            elif component_name == "conversation_handler":
                optimizer = await registry.get("optimizer")
                if optimizer:
                    return ConversationHandler(optimizer=optimizer, config=config.get('conversation', {}))

            elif component_name == "protocol_handler":
                optimizer = await registry.get("optimizer")
                rate_limiter = await registry.get("rate_limiter")
                return ProtocolHandler(optimizer=optimizer, dependencies={"rate_limiter": rate_limiter}, config=config, logger=logger)

            elif component_name == "transport_manager":
                conversation_handler = await registry.get("conversation_handler")
                protocol_handler = await registry.get("protocol_handler")
                return TransportManager(server=None, protocol_handler=protocol_handler, conversation_handler=conversation_handler, config=config.get('transport', {}))

            elif component_name == "connection_manager":
                transport_manager = await registry.get("transport_manager")
                protocol_handler = await registry.get("protocol_handler")
                rate_limiter = await registry.get("rate_limiter")
                from .connection import ConnectionManager
                return ConnectionManager(config=config.get('connection', {}), logger=logger, dependencies={"transport_manager": transport_manager, "protocol_handler": protocol_handler, "rate_limiter": rate_limiter})

            elif component_name == "session_manager":
                protocol_handler = await registry.get("protocol_handler")
                connection_manager = await registry.get("connection_manager")
                from .session_manager import SessionManager
                return SessionManager(config=config.get('session', {}), logger=logger, server=None, dependencies={"protocol_handler": protocol_handler, "connection_manager": connection_manager})

        except (ValueError, TypeError) as e:
            logger.error(f"Configuration error creating {component_name}: {e}")
            raise InitializationError(f"Configuration error creating {component_name}: {str(e)}")

        except ProtocolError as e:
            logger.error(f"Protocol error creating {component_name}: {e}")
            raise

        except Exception as e:
            logger.error(f"Failed to create component {component_name}: {e}")
            raise InitializationError(f"Component creation for {component_name} failed: {str(e)}")

    @classmethod
    async def _create_server_instance(
        cls,
        config: Dict[str, Any],
        logger: logging.Logger,
        registry: ComponentRegistry
    ) -> ServerInterface:
        """Create the server instance with all components."""
        from .main import MCPServer

        try:
            # Get all required components
            protocol_handler = await registry.get("protocol_handler")
            session_manager = await registry.get("session_manager")
            connection_manager = await registry.get("connection_manager")
            transport_manager = await registry.get("transport_manager")
            rate_limiter = await registry.get("rate_limiter")
            optimizer = await registry.get("optimizer")
            conversation_handler = await registry.get("conversation_handler")

            # Create server instance
            server = MCPServer(
                config=config,
                logger=logger,
                protocol_handler=protocol_handler,
                session_manager=session_manager,
                connection_manager=connection_manager,
                transport_manager=transport_manager,
                rate_limiter=rate_limiter,
                optimizer=optimizer,
                conversation_handler=conversation_handler
            )

            # Set server for components that use it
            if session_manager:
                session_manager.server = server
            if transport_manager:
                transport_manager.server = server

            # Initialize server
            if not await server.initialize():
                raise InitializationError("Server initialization failed")

            return server

        except Exception as e:
            logger.error(f"Server instance creation failed: {e}")
            raise InitializationError(f"Server creation failed: {str(e)}")

    @classmethod
    async def validate_config(cls, config: Dict[str, Any], logger: logging.Logger) -> List[str]:
        """Validate server configuration."""
        issues = []

        try:
            # Validate required sections
            required_sections = {'rate_limiter', 'optimizer', 'transport', 'connection', 'session'}
            missing = required_sections - set(config.keys())
            if missing:
                issues.append(f"Missing required configuration sections: {missing}")

            # Validate transport config
            if 'transport' in config:
                issues.extend(await cls._validate_transport_config(config['transport'], logger))

            # Validate rate limiter config
            rate_limit_config = config.get('rate_limiter', {})
            if not isinstance(rate_limit_config.get('tokens_per_second'), (int, float)):
                issues.append("rate_limiter.tokens_per_second must be a number")
            if not isinstance(rate_limit_config.get('burst_size'), int):
                issues.append("rate_limiter.burst_size must be an integer")

            # Validate optimizer config
            optimizer_config = config.get('optimizer_config', {})
            if not isinstance(optimizer_config.get('max_prompt_length'), int):
                issues.append("optimizer_config.max_prompt_length must be an integer")
            if not isinstance(optimizer_config.get('semantic_threshold'), (int, float)):
                issues.append("optimizer_config.semantic_threshold must be a number")

            # Validate optimizer config more deeply
            if 'optimizer_config' in config:
                issues.extend(await cls._validate_optimizer_config(config['optimizer_config'], logger))

            # Validate session config
            if 'session' in config:
                issues.extend(await cls._validate_session_config(config['session'], logger))

            return issues

        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            issues.append(f"Validation error: {str(e)}")
            return issues

    @classmethod
    async def _validate_transport_config(cls, transport_config: Dict[str, Any], logger: logging.Logger) -> List[str]:
        issues = []
        if 'type' in transport_config:
            try:
                TransportType(transport_config['type'])
            except ValueError:
                issues.append(f"Invalid transport type: {transport_config.get('type')}")
        else:
            issues.append("Missing 'type' in transport configuration")

        if transport_config.get('type') == 'stdio':
            stdio_config = transport_config.get('stdio_config', {})
            required_keys = ['buffer_size', 'encoding']
            missing_keys = [key for key in required_keys if key not in stdio_config]
            if missing_keys:
                issues.append(f"Missing required keys in stdio_config: {', '.join(missing_keys)}")
            if 'buffer_size' in stdio_config and not isinstance(stdio_config['buffer_size'], int):
                issues.append('stdio_config.buffer_size must be an integer')
            if 'encoding' in stdio_config and not isinstance(stdio_config['encoding'], str):
                issues.append('stdio_config.encoding must be a string')

        elif transport_config.get('type') == 'websocket':
            websocket_config = transport_config.get('websocket_config', {})
            required_keys = ['host', 'port']
            missing_keys = [key for key in required_keys if key not in websocket_config]
            if missing_keys:
                issues.append(f"Missing required keys in websocket_config: {', '.join(missing_keys)}")
            if 'host' in websocket_config and not isinstance(websocket_config['host'], str):
                issues.append('websocket_config.host must be a string')
            if 'port' in websocket_config and not isinstance(websocket_config['port'], int):
                issues.append('websocket_config.port must be an integer')
        return issues

    @classmethod
    async def _validate_optimizer_config(cls, optimizer_config: Dict[str, Any], logger: logging.Logger) -> List[str]:
        issues = []

        if 'dspy_config' in optimizer_config:
            dspy_config = optimizer_config['dspy_config']
            if 'model_name' not in dspy_config:
                issues.append("dspy_config.model_name is required")
            elif not isinstance(dspy_config['model_name'], str):
                issues.append("dspy_config.model_name must be a string")

            if 'temperature' in dspy_config and not isinstance(dspy_config['temperature'], (int, float)):
                issues.append("dspy_config.temperature must be a number")
            elif 'temperature' in dspy_config and not (0.0 <= dspy_config['temperature'] <= 1.0):
                issues.append("dspy_config.temperature must be between 0.0 and 1.0")

            # You can add more checks for other dspy_config fields
        else:
            issues.append('optimizer_config.dspy_config is required')

        return issues

    @classmethod
    async def _validate_session_config(cls, session_config: Dict[str, Any], logger: logging.Logger) -> List[str]:
        issues = []

        required_keys = ['timeout_seconds', 'cleanup_interval_seconds']
        missing_keys = [key for key in required_keys if key not in session_config]
        if missing_keys:
            issues.append(f"Missing required keys in session configuration: {', '.join(missing_keys)}")

        if 'timeout_seconds' in session_config and not isinstance(session_config['timeout_seconds'], int):
            issues.append("session.timeout_seconds must be an integer")

        if 'cleanup_interval_seconds' in session_config and not isinstance(session_config['cleanup_interval_seconds'], int):
            issues.append("session.cleanup_interval_seconds must be an integer")

        return issues

# Export classes for use in other modules
__all__ = [
    "ServerInitializer",
    "ComponentRegistry",
    "InitializationError",
    "ResourceError",
    "ComponentError"
]
