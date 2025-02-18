import asyncio
import logging
import json
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, AsyncIterator, Union, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import threading
import weakref
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import dotenv
from functools import lru_cache
from filelock import FileLock
import psutil

from .shared_types import (
    ProcessingLevel,
    ValidationLevel,
    RateLimitConfig,
    OptimizerConfig,
    MessagingConfig,
    TransportType,
    ProtocolError,
    ErrorCodes,
    ComponentState,
    RateLimitState,
    TransportMetrics
)
from .interfaces import (
    ConfigInterface,
    ValidationInterface,
    RateLimiterInterface
)

# --- Configuration Exceptions ---

class ConfigurationError(Exception):
    """Base exception for configuration-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class ValidationError(ConfigurationError):
    """Exception for configuration validation errors."""
    pass

class RuntimeUpdateError(ConfigurationError):
    """Exception for runtime update failures."""
    pass

# --- Core Data Models ---

@dataclass
class ConfigMetrics:
    """Configuration metrics aligned with system metric patterns."""
    total_updates: int = 0
    error_count: int = 0
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    component_updates: Dict[str, int] = field(default_factory=dict)
    active_sources: int = 0
    runtime_updates: int = 0
    validation_failures: int = 0

    def record_update(self, component: str) -> None:
        """Record a configuration update."""
        self.total_updates += 1
        self.last_update = datetime.now(timezone.utc)
        self.component_updates[component] = self.component_updates.get(component, 0) + 1

    def record_error(self) -> None:
        """Record an error occurrence."""
        self.error_count += 1

@dataclass
class ConfigurationSource:
    """Configuration source with validation and locking."""
    name: str
    priority: int
    path: Optional[Path] = None
    data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _file_lock: Optional[FileLock] = None

    async def validate(self) -> List[str]:
        """Validate configuration source."""
        issues = []
        async with self._lock:
            if self.priority < 0 or self.priority > 100:
                issues.append("Priority must be between 0 and 100")
            if self.path and not self.path.parent.exists():
                issues.append(f"Path parent directory does not exist: {self.path.parent}")
            if self.path and self.path.exists() and not os.access(self.path, os.R_OK):
                issues.append(f"Cannot read configuration file: {self.path}")
        return issues

    async def update(self, data: Dict[str, Any]) -> None:
        """Update source data atomically."""
        async with self._lock:
            if self._file_lock and self.path:
                with self._file_lock:
                    self.data = data
                    self.last_updated = datetime.now(timezone.utc)
                    # Write to file if it's a file source
                    if self.path.suffix == '.json':
                        with open(self.path, 'w') as f:
                            json.dump(data, f, indent=2)
                    else:
                        with open(self.path, 'w') as f:
                            yaml.safe_dump(data, f)
            else:
                self.data = data
                self.last_updated = datetime.now(timezone.utc)

class ConfigVersionControl:
    """Version control for configuration changes."""
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self._lock = asyncio.Lock()

    async def add_version(self, config: Dict[str, Any]) -> None:
        """Add new configuration version."""
        async with self._lock:
            self.history.append({
                'timestamp': datetime.now(timezone.utc),
                'config': config.copy()
            })
            if len(self.history) > self.max_history:
                self.history.pop(0)

    async def get_version(self, index: int = -1) -> Optional[Dict[str, Any]]:
        """Get specific configuration version."""
        async with self._lock:
            if not self.history:
                return None
            try:
                return self.history[index]['config']
            except IndexError:
                return None

    async def rollback(self) -> Optional[Dict[str, Any]]:
        """Rollback to previous configuration version."""
        async with self._lock:
            if len(self.history) < 2:
                return None
            self.history.pop()  # Remove current version
            return self.history[-1]['config']

class RuntimeValidator:
    """Validates runtime configuration changes."""

    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self._setup_validators()

    def _setup_validators(self):
        """Set up component-specific validators."""
        self.validators = {
            'rate_limiter': self._validate_rate_limiter,
            'optimizer': self._validate_optimizer,
            'transport': self._validate_transport,
            'connection': self._validate_connection,
            'session': self._validate_session
        }

    async def validate_component(self, component: str, config: Dict[str, Any]) -> List[str]:
        """Validate component-specific configuration."""
        validator = self.validators.get(component)
        if not validator:
            return [f"No validator found for component: {component}"]
        return await validator(config)

    async def _validate_rate_limiter(self, config: Dict[str, Any]) -> List[str]:
        """Validate rate limiter configuration."""
        issues = []
        if not isinstance(config.get('tokens_per_second'), (int, float)):
            issues.append("tokens_per_second must be a number")
        if not isinstance(config.get('burst_size'), int):
            issues.append("burst_size must be an integer")
        if 'window_seconds' not in config:
            issues.append("window_seconds is required")
        if 'size_thresholds' not in config:
            issues.append("size_thresholds configuration is required")
        return issues

    async def _validate_optimizer(self, config: Dict[str, Any]) -> List[str]:
        """Validate optimizer configuration."""
        issues = []
        if not isinstance(config.get('max_prompt_length'), int):
            issues.append("max_prompt_length must be an integer")
        if not isinstance(config.get('semantic_threshold'), (int, float)):
            issues.append("semantic_threshold must be a number")
        return issues

    async def _validate_transport(self, config: Dict[str, Any]) -> List[str]:
        """Validate transport configuration."""
        issues = []
        transport_type = config.get('type')
        if transport_type not in [t.value for t in TransportType]:
            issues.append(f"Invalid transport type: {transport_type}")

        # Validate additional transport settings
        if transport_type == TransportType.WEBSOCKET.value:
            if 'host' not in config:
                issues.append("WebSocket host is required")
            if 'port' not in config:
                issues.append("WebSocket port is required")
        elif transport_type == TransportType.STDIO.value:
            if sys.platform == "win32" and not config.get('binary_mode', False):
                issues.append("binary_mode must be True for STDIO on Windows")

        return issues

    async def _validate_connection(self, config: Dict[str, Any]) -> List[str]:
        """Validate connection configuration."""
        issues = []
        required_fields = {
            'max_message_size',
            'timeout',
            'max_retries',
            'retry_delay',
            'max_connections'
        }
        missing = required_fields - set(config.keys())
        if missing:
            issues.append(f"Missing required fields: {missing}")

        # Validate specific fields
        if not isinstance(config.get('max_connections'), int):
            issues.append("max_connections must be an integer")
        if not isinstance(config.get('timeout'), (int, float)):
            issues.append("timeout must be a number")
        if not isinstance(config.get('max_retries'), int):
            issues.append("max_retries must be an integer")
        if not isinstance(config.get('retry_delay'), (int, float)):
            issues.append("retry_delay must be a number")

        return issues

    async def _validate_session(self, config: Dict[str, Any]) -> List[str]:
        """Validate session configuration."""
        issues = []
        if not isinstance(config.get('timeout_seconds'), int):
            issues.append("timeout_seconds must be an integer")
        if not isinstance(config.get('cleanup_interval_seconds'), int):
            issues.append("cleanup_interval_seconds must be an integer")
        return issues

class ConfigFileHandler(FileSystemEventHandler):
    """Enhanced file system event handler for configuration."""
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self._debounce_timer: Optional[asyncio.TimerHandle] = None
        self._debounce_delay = 0.5  # seconds

    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification with debouncing."""
        if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml')):
            if self._debounce_timer:
                self._debounce_timer.cancel()

            loop = asyncio.get_event_loop()
            self._debounce_timer = loop.call_later(
                self._debounce_delay,
                lambda: asyncio.create_task(self._handle_modification(event.src_path))
            )

    async def _handle_modification(self, path: str):
        """Handle configuration file modification."""
        try:
            await self.config_manager.reload_configuration()
            self.logger.info(f"Configuration reloaded after changes to {path}")
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")

class ConfigManager(ConfigInterface, ValidationInterface):
    """Complete configuration manager implementation."""

    def __init__(self, base_path: Path):
        """Initialize configuration manager."""
        self.base_path = base_path.resolve()
        self.logger = logging.getLogger(__name__)

        # Storage
        self.sources: Dict[str, ConfigurationSource] = {}
        self.current_config: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

        # Version control
        self.version_control = ConfigVersionControl()

        # Validation
        self.runtime_validator = RuntimeValidator()

        # Component state
        self.component_state = ComponentState.UNINITIALIZED

        # File monitoring
        self.file_observer = Observer()
        self.file_handler = ConfigFileHandler(self)
        self._file_locks: Dict[Path, FileLock] = {}

        # Change notification
        self.observers: Set[Callable] = set()

        # Metrics
        self.metrics = ConfigMetrics()

        # Resource monitoring
        self._memory_monitor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Initialize configuration manager."""
        try:
            async with self._lock:
                self.component_state = ComponentState.INITIALIZING

                # Load environment variables
                await self._load_environment()

                # Load configuration files
                await self._load_config_files()

                # Start file monitoring
                self._start_file_monitoring()

                # Start background tasks
                self._memory_monitor_task = asyncio.create_task(self._monitor_memory())
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())

                self.component_state = ComponentState.READY
                return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def _load_environment(self):
        """Load environment variables."""
        env_file = self.base_path / '.env'
        if env_file.exists():
            dotenv.load_dotenv(env_file)

        # Get configuration-related environment variables
        config_vars = {
            key: value for key, value in dotenv.dotenv_values().items()
            if key.startswith(('CONFIG_', 'APP_', 'MCP_'))
        }

        if config_vars:
            self.sources['environment'] = ConfigurationSource(
                name='environment',
                priority=100,
                data=config_vars
            )
            self.metrics.active_sources += 1

    async def _load_config_files(self):
        """Load configuration from files with locking."""
        for file_path in self.base_path.glob('*'):
            if file_path.suffix not in {'.json', '.yaml', '.yml'}:
                continue

            lock_path = file_path.with_suffix(file_path.suffix + '.lock')
            self._file_locks[file_path] = FileLock(lock_path)

            try:
                with self._file_locks[file_path]:
                    with open(file_path, 'r') as f:
                        data = (
                            json.load(f) if file_path.suffix == '.json'
                            else yaml.safe_load(f)
                        )

                    self.sources[file_path.stem] = ConfigurationSource(
                        name=file_path.stem,
                        priority=50,
                        path=file_path,
                        data=data,
                        _file_lock=self._file_locks[file_path]
                    )
                    self.logger.debug(f"Loaded configuration from {file_path}")
                    self.metrics.active_sources += 1

            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                self.metrics.record_error()

    def _start_file_monitoring(self):
        """Start configuration file monitoring."""
        self.file_observer.schedule(
            self.file_handler,
            str(self.base_path),
            recursive=False
        )
        self.file_observer.start()

    async def update_component_config(
        self,
        component: str,
        updates: Dict[str, Any],
        notify: bool = True
    ) -> None:
        """Update component configuration at runtime."""
        async with self._lock:
            try:
                # Validate updates
                issues = await self.runtime_validator.validate_component(
                    component,
                    updates
                )
                if issues:
                    raise ValidationError(f"Invalid configuration: {issues}")

                # Create backup
                await self.version_control.add_version(self.current_config)

                # Apply updates
                if component not in self.current_config:
                    self.current_config[component] = {}
                self.current_config[component].update(updates)

                # Update metrics
                self.metrics.record_update(component)
                self.metrics.runtime_updates += 1

                # Notify observers
                if notify:
                    await self._notify_observers({
                        'component': component,
                        'updates': updates,
                        'timestamp': datetime.now(timezone.utc)
                    })

            except Exception as e:
                self.logger.error(f"Update failed: {e}")
                self.metrics.record_error()
                # Attempt rollback
                previous_config = await self.version_control.rollback()
                if previous_config:
                    self.current_config = previous_config
                raise RuntimeUpdateError(f"Configuration update failed: {str(e)}")

    async def get_component_config(self, component: str) -> Dict[str, Any]:
        """Get configuration for a specific component."""
        async with self._lock:
            if component not in self.current_config:
                raise ConfigurationError(f"No configuration found for component: {component}")
            return self.current_config[component].copy()

    async def validate_configuration(self) -> List[str]:
        """Validate the entire configuration."""
        issues = []

        try:
            # Validate component configs
            for component, config in self.current_config.items():
                component_issues = await self.runtime_validator.validate_component(
                    component,
                    config
                )
                if component_issues:
                    issues.extend(f"{component}: {issue}" for issue in component_issues)

            # Validate required sections
            required_sections = {'rate_limiter', 'optimizer', 'transport'}
            missing = required_sections - set(self.current_config.keys())
            if missing:
                issues.append(f"Missing required sections: {missing}")

            # Cross-component validation
            await self._validate_cross_component_dependencies(issues)

            return issues

        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            self.metrics.validation_failures += 1
            issues.append(f"Validation error: {str(e)}")
            return issues

    async def _validate_cross_component_dependencies(self, issues: List[str]) -> None:
        """Validate dependencies between components."""
        try:
            if 'rate_limiter' in self.current_config and 'optimizer' in self.current_config:
                rate_limit = self.current_config['rate_limiter']
                optimizer = self.current_config['optimizer']

                # Example: Ensure rate limit window is appropriate for optimizer timeout
                if rate_limit.get('window_seconds', 0) > optimizer.get('timeout_seconds', 0):
                    issues.append("Rate limit window should not exceed optimizer timeout")

            # Validate transport dependencies
            if 'transport' in self.current_config:
                transport = self.current_config['transport']
                if transport.get('type') == TransportType.WEBSOCKET.value:
                    if 'connection' not in self.current_config:
                        issues.append("WebSocket transport requires connection configuration")

        except Exception as e:
            self.logger.error(f"Cross-component validation error: {e}")
            issues.append(f"Cross-component validation error: {str(e)}")

    async def reload_configuration(self) -> None:
        """Reload configuration from all sources."""
        async with self._lock:
            try:
                # Store old config for comparison
                old_config = self.current_config.copy()

                # Reload from all sources
                await self._load_config_files()

                # Re-initialize component configs
                self.current_config = await self._merge_configurations()

                # Validate new configuration
                issues = await self.validate_configuration()
                if issues:
                    raise ValidationError(f"Configuration validation failed: {issues}")

                # Update metrics
                self.metrics.total_updates += 1
                self.metrics.last_update = datetime.now(timezone.utc)

                # Notify observers of changes
                await self._notify_observers({
                    'type': 'reload',
                    'old_config': old_config,
                    'new_config': self.current_config,
                    'timestamp': datetime.now(timezone.utc)
                })

                self.logger.info("Configuration reloaded successfully")

            except Exception as e:
                self.metrics.record_error()
                self.logger.error(f"Configuration reload failed: {e}")
                raise

    async def _merge_configurations(self) -> Dict[str, Any]:
        """Merge configurations from all sources based on priority."""
        merged = {}
        sources = sorted(
            self.sources.values(),
            key=lambda s: s.priority,
            reverse=True
        )

        for source in sources:
            self._deep_merge(merged, source.data)

        return merged

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge source into target."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    async def _monitor_memory(self) -> None:
        """Monitor memory usage of configuration manager."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                process = psutil.Process()
                memory_percent = process.memory_percent()

                if memory_percent > 90:  # Critical threshold
                    self.logger.warning("Critical memory usage detected")
                    await self._handle_critical_memory()
                elif memory_percent > 80:  # Warning threshold
                    self.logger.warning("High memory usage detected")
                    await self._handle_high_memory()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")

    async def _handle_critical_memory(self) -> None:
        """Handle critical memory usage."""
        async with self._lock:
            # Clear version history
            self.version_control.history.clear()

            # Clear non-essential metrics
            self.metrics.component_updates.clear()

            # Force garbage collection
            import gc
            gc.collect()

    async def _handle_high_memory(self) -> None:
        """Handle high memory usage."""
        async with self._lock:
            # Trim version history
            while len(self.version_control.history) > 5:
                self.version_control.history.pop(0)

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of resources."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                async with self._lock:
                    # Clean up file locks
                    for path, lock in list(self._file_locks.items()):
                        if not path.exists():
                            lock.release()
                            del self._file_locks[path]

                    # Clean up inactive observers
                    for observer in list(self.observers):
                        if not observer:
                            self.observers.discard(observer)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

    async def _notify_observers(self, change_info: Dict[str, Any]) -> None:
        """Notify configuration change observers."""
        for observer in list(self.observers):
            try:
                await observer(change_info)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {e}")
                self.observers.discard(observer)  # Remove failed observer

    @asynccontextmanager
    async def component_config_context(self, component: str):
        """Context manager for temporary component configuration modifications."""
        original_config = None
        try:
            async with self._lock:
                if component in self.current_config:
                    original_config = self.current_config[component].copy()
            yield
        finally:
            if original_config:
                await self.update_component_config(
                    component,
                    original_config,
                    notify=False
                )

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive configuration metrics."""
        return {
            "updates": {
                "total": self.metrics.total_updates,
                "runtime": self.metrics.runtime_updates,
                "last_update": (
                    self.metrics.last_update.isoformat()
                    if self.metrics.last_update else None
                ),
                "component_updates": dict(self.metrics.component_updates)
            },
            "errors": {
                "total": self.metrics.error_count,
                "validation_failures": self.metrics.validation_failures
            },
            "sources": {
                "active": self.metrics.active_sources,
                "details": {
                    name: {
                        "priority": source.priority,
                        "last_updated": source.last_updated.isoformat(),
                        "path": str(source.path) if source.path else None
                    }
                    for name, source in self.sources.items()
                }
            },
            "state": {
                "component_state": self.component_state.value,
                "version_history_size": len(self.version_control.history),
                "observers": len(self.observers)
            }
        }

    async def cleanup(self) -> None:
        """Complete cleanup of configuration manager resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Cancel background tasks
            for task in [self._memory_monitor_task, self._cleanup_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

            # Stop file monitoring
            self.file_observer.stop()
            self.file_observer.join()

            # Release file locks
            for lock in self._file_locks.values():
                if lock.is_locked:
                    lock.release()

            # Clear collections
            self.sources.clear()
            self.current_config.clear()
            self.observers.clear()
            self.version_control.history.clear()

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Configuration manager cleanup complete")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.component_state = ComponentState.ERROR
            raise

    async def is_healthy(self) -> bool:
        """Check if configuration manager is healthy."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            if not self.file_observer.is_alive():
                return False

            if not all(
                source.path.exists()
                for source in self.sources.values()
                if source.path is not None
            ):
                return False

            # Check background tasks
            if any(
                task and task.done()
                for task in [self._memory_monitor_task, self._cleanup_task]
            ):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
