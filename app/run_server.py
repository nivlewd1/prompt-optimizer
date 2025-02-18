import asyncio
import logging
import sys
import os
import json
import psutil
import signal
import random
import tempfile  # Need to add this for cleanup_sequence
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, DefaultDict
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

import aiofiles
import argparse

# Add the path to the project root directory, not app/
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from .main import MCPServer
from .initialization import ServerInitializer
from .config_manager import ConfigManager, ConfigurationError
from .shared_types import (
    ProtocolError,
    ErrorCodes,
    PROTOCOL_VERSION,
    MINIMAL_COMPATIBLE_VERSION,
    MCPVersion,
    MessageStream,
    ComponentState
)
from .utils.json_utils import dumps_with_datetime
from .interfaces import MetricsInterface

# ----------------------------------------------------------------------------
# Enhanced Metrics System
# ----------------------------------------------------------------------------

@dataclass
class MetricsError:
    """Enhanced error tracking for metrics collection."""
    timestamp: datetime
    error_type: str
    component: str
    message: str
    stacktrace: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricsWindow:
    """Ring buffer implementation for sliding window metrics."""
    window_size: int
    data: List[Tuple[datetime, Dict[str, Any]]] = field(default_factory=list)

    def add_metric(self, metric: Dict[str, Any]) -> None:
        """Add metric with timestamp."""
        now = datetime.now(timezone.utc)
        self.data.append((now, metric))
        # Cleanup old data
        cutoff = now - timedelta(minutes=self.window_size)
        self.data = [x for x in self.data if x[0] > cutoff]

    def get_average(self) -> Dict[str, Any]:
        """Calculate window average."""
        if not self.data:
            return {}

        result = defaultdict(float)
        for _, metric in self.data:
            for key, value in metric.items():
                if isinstance(value, (int, float)):
                    result[key] += value

        for key in result:
            result[key] /= len(self.data)

        return dict(result)

class MetricsCollector:
    """Enhanced metrics collector with backpressure."""
    def __init__(self, max_memory_mb: int = 100):
        self.windows = {
            1: MetricsWindow(1),   # 1 minute
            5: MetricsWindow(5),   # 5 minutes
            15: MetricsWindow(15)  # 15 minutes
        }
        self.errors: List[MetricsError] = []
        self.max_memory_mb = max_memory_mb
        self.queue = asyncio.Queue(maxsize=1000)  # Backpressure queue
        self._memory_check_task: Optional[asyncio.Task] = None

    def _check_memory_usage(self) -> bool:
        """Check if metrics collection is using too much memory."""
        try:
            process = psutil.Process()
            metrics_memory = process.memory_info().rss / (1024 * 1024)  # MB
            return metrics_memory < self.max_memory_mb
        except Exception:
            return False

    async def record_error(
        self,
        error_type: str,
        component: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record detailed error information."""
        import traceback
        error_info = MetricsError(
            timestamp=datetime.now(timezone.utc),
            error_type=error_type,
            component=component,
            message=str(error),
            stacktrace=traceback.format_exc(),
            metadata=metadata or {}
        )
        self.errors.append(error_info)

        # Keep only last 1000 errors
        if len(self.errors) > 1000:
            self.errors = self.errors[-1000:]

# ----------------------------------------------------------------------------
# Windows Resource Management
# ----------------------------------------------------------------------------

@dataclass
class WindowsResourceMetrics:
    """Track Windows-specific resource usage."""
    handle_count: int = 0
    gdi_objects: int = 0
    user_objects: int = 0
    peak_handle_count: int = 0
    last_cleanup: Optional[datetime] = None
    cleanup_count: int = 0

class WindowsResourceManager:
    """Manage Windows-specific resources and handle cleanup."""
    def __init__(
        self,
        handle_threshold: int = 1000,
        cleanup_interval: int = 300,  # 5 minutes
        logger: Optional[logging.Logger] = None
    ):
        self.handle_threshold = handle_threshold
        self.cleanup_interval = cleanup_interval
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = WindowsResourceMetrics()
        self._lock = asyncio.Lock()
        self._last_check = datetime.now(timezone.utc)

    async def check_resources(self) -> bool:
        """Check Windows resource usage."""
        if sys.platform != "win32":
            return True

        try:
            async with self._lock:
                process = psutil.Process()

                # Update metrics
                self.metrics.handle_count = process.num_handles()
                self.metrics.peak_handle_count = max(
                    self.metrics.peak_handle_count,
                    self.metrics.handle_count
                )

                # Check if cleanup is needed
                if self.metrics.handle_count > self.handle_threshold:
                    await self._cleanup_resources()
                    return False

                return True

        except Exception as e:
            self.logger.error(f"Error checking Windows resources: {e}")
            return False

    async def _cleanup_resources(self):
        """Clean up Windows resources."""
        try:
            process = psutil.Process()

            # Close file handles
            for handler in process.open_files():
                try:
                    os.close(handler.fd)
                except Exception as e:
                    self.logger.debug(f"Failed to close file handle: {e}")

            # Force garbage collection
            import gc
            gc.collect()

            self.metrics.cleanup_count += 1
            self.metrics.last_cleanup = datetime.now(timezone.utc)

        except Exception as e:
            self.logger.error(f"Error cleaning up Windows resources: {e}")

class ResourceMonitor:
    """Monitor system resources with Windows-specific handling."""
    def __init__(
        self,
        server: MCPServer,
        logger: logging.Logger,
        windows_resource_manager: Optional[WindowsResourceManager] = None
    ):
        self.server = server
        self.logger = logger
        self.windows_resource_manager = windows_resource_manager
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start_monitoring(self):
        """Start resource monitoring."""
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Stop resource monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                # Check system resources
                process = psutil.Process()
                system_metrics = {
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds(),
                }

                # Windows-specific checks
                if sys.platform == "win32" and self.windows_resource_manager:
                    if not await self.windows_resource_manager.check_resources():
                        self.logger.warning("Windows resource threshold exceeded")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause on error

# ----------------------------------------------------------------------------
# Server Lifecycle Management
# ----------------------------------------------------------------------------

class ServerLifecycle:
    """Manage server lifecycle with enhanced state tracking."""

    def __init__(
        self,
        server: MCPServer,
        config_manager: ConfigManager,
        logger: logging.Logger
    ):
        self.server = server
        self.config_manager = config_manager
        self.logger = logger
        self.start_time = datetime.now(timezone.utc)
        self.shutdown_requested = False
        self._tasks: List[asyncio.Task] = []

    async def initialize(self) -> bool:
        """Initialize server with enhanced error handling."""
        try:
            # Create and track background tasks
            metrics_task = asyncio.create_task(
                metrics_collector(self.server, self.logger, 60)
            )
            self._tasks.append(metrics_task)

            health_check = HealthCheck(self.server, self.logger)
            health_task = asyncio.create_task(
                health_check_monitor(health_check, self.logger, 60)
            )
            self._tasks.append(health_task)

            # Windows-specific initialization
            if sys.platform == "win32":
                windows_resource_manager = WindowsResourceManager(
                    handle_threshold=self.server.config.get(
                        "windows_handle_threshold", 1000
                    ),
                    logger=self.logger
                )
                resource_monitor = ResourceMonitor(
                    self.server,
                    self.logger,
                    windows_resource_manager
                )
                await resource_monitor.start_monitoring()

            return True

        except Exception as e:
            self.logger.error(f"Server initialization failed: {e}")
            await self.cleanup()
            return False

    async def cleanup(self) -> None:
        """Enhanced cleanup with proper task handling."""
        self.shutdown_requested = True

        # Cancel all background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    self.logger.error(f"Error cancelling task: {e}")

        try:
            # Cleanup server resources
            await cleanup_sequence(
                self.server,
                self.logger,
                self.config_manager
            )
        except Exception as e:
            self.logger.error(f"Cleanup sequence failed: {e}")
            raise

# ----------------------------------------------------------------------------
# Recovery and Configuration Management
# ----------------------------------------------------------------------------

async def attempt_recovery(
    server: MCPServer,
    logger: logging.Logger,
    config_manager: Optional[ConfigManager] = None,
    max_attempts: int = 3
) -> bool:
    """Enhanced recovery with configuration state preservation."""
    last_working_config = None
    if config_manager:
        last_working_config = config_manager.current_config.copy()

    for attempt in range(max_attempts):
        try:
            logger.warning(f"Starting recovery attempt {attempt + 1}/{max_attempts}")

            # Try to reinitialize components in order
            components = [
                'session_manager',
                'connection_manager',
                'transport_manager',
                'metrics_collector'
            ]

            for component in components:
                success = await server._attempt_component_recovery(component)
                if not success:
                    logger.error(f"Failed to recover {component}")
                    break

            # Verify system health
            if await server.is_healthy():
                logger.info("Server recovery successful")
                return True

            # Brief pause between attempts
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

        except Exception as e:
            logger.error(f"Recovery attempt {attempt + 1} failed: {e}")
            if last_working_config and config_manager:
                try:
                    # Attempt config rollback
                    config_manager.current_config = last_working_config
                    await server.update_config(last_working_config)
                except Exception as ce:
                    logger.error(f"Config rollback failed: {ce}")

    return False

async def reload_config(
    server: MCPServer,
    config_manager: ConfigManager,
    logger: logging.Logger
) -> bool:
    """Enhanced configuration reload with validation and rollback."""
    previous_config = config_manager.current_config.copy()

    try:
        logger.info("Starting configuration reload...")

        # Load and validate new configuration
        await config_manager.reload_configuration()
        validation_errors = await config_manager.validate_configuration()

        if validation_errors:
            raise ConfigurationError(
                f"Configuration validation failed:\n" + "\n".join(validation_errors)
            )

        # Apply new configuration with validation
        new_config = config_manager.current_config
        try:
            # Verify critical settings
            await _verify_critical_config(new_config, logger)

            # Update server configuration
            await server.update_config(new_config)

            # Verify system health after update
            if not await server.is_healthy():
                raise ConfigurationError("Server health check failed after config update")

            logger.info("Configuration reloaded successfully")
            return True

        except Exception as e:
            # Rollback to previous configuration
            logger.error(f"Configuration update failed: {e}")
            config_manager.current_config = previous_config
            await server.update_config(previous_config)
            return False

    except Exception as e:
        logger.error(f"Configuration reload failed: {e}")
        config_manager.current_config = previous_config
        return False

async def _verify_critical_config(config: Dict[str, Any], logger: logging.Logger) -> None:
    """Verify critical configuration settings."""
    critical_keys = {
        'transport': {'type', 'port'},
        'rate_limiter': {'tokens_per_second', 'burst_size'},
        'session': {'timeout_seconds', 'cleanup_interval_seconds'}
    }

    for section, required_keys in critical_keys.items():
        if section not in config:
            raise ConfigurationError(f"Missing critical section: {section}")

        section_config = config[section]
        missing_keys = required_keys - set(section_config.keys())
        if missing_keys:
            raise ConfigurationError(
                f"Missing critical keys in {section}: {missing_keys}"
            )

# ----------------------------------------------------------------------------
# Main Entry Point and Server Run Functions
# ----------------------------------------------------------------------------

async def metrics_collector(
    server: MCPServer,
    logger: logging.Logger,
    interval: int,
    versioned: bool = True
):
    """Enhanced metrics collection with backpressure."""
    collector = MetricsCollector()

    async def process_metrics_queue():
        """Process metrics queue with backpressure."""
        while True:
            try:
                metrics = await collector.queue.get()

                if collector._check_memory_usage():
                    # Update windows and collect averages
                    for window in collector.windows.values():
                        window.add_metric(metrics)

                    windowed_metrics = {
                        f"{size}min_avg": window.get_average()
                        for size, window in collector.windows.items()
                    }

                    if server.metrics_collector:
                        await server.metrics_collector.collect_metrics({
                            "version": "1.0.0",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "current": metrics,
                            "averages": windowed_metrics,
                            "errors": [error.__dict__ for error in collector.errors[-10:]]
                        })
                else:
                    logger.warning("Metrics collection suspended due to memory pressure")

                collector.queue.task_done()

            except Exception as e:
                await collector.record_error(
                    "METRICS_PROCESSING",
                    "metrics_collector",
                    e,
                    {"queue_size": collector.queue.qsize()}
                )
                logger.error(f"Error processing metrics: {e}")

    # Start queue processor
    queue_task = asyncio.create_task(process_metrics_queue())

    try:
        while not server.shutdown_event.is_set():
            try:
                metrics = await server._aggregate_metrics()

                try:
                    # Add to queue with timeout to prevent blocking
                    await asyncio.wait_for(
                        collector.queue.put(metrics),
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    logger.warning("Metrics queue full - dropping metrics")
                    await collector.record_error(
                        "QUEUE_FULL",
                        "metrics_collector",
                        Exception("Queue full"),
                        {"queue_size": collector.queue.qsize()}
                    )

            except Exception as e:
                await collector.record_error(
                    "METRICS_COLLECTION",
                    "metrics_collector",
                    e
                )
                logger.error(f"Error collecting metrics: {e}")

            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        logger.debug("Metrics collection cancelled")
    finally:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass

async def main():
    """Enhanced main function with proper lifecycle management."""
    logger: Optional[logging.Logger] = None
    server: Optional[MCPServer] = None
    lifecycle: Optional[ServerLifecycle] = None

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the MCP server.")
    parser.add_argument(
        "--config_dir",
        default=None,
        help="Directory containing configuration files for the ConfigManager."
    )
    parser.add_argument(
        "--log_level",
        default="INFO",
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    parser.add_argument(
        "--log_file",
        default=None,
        help="Path to a log file for rotating file logging."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval (in seconds) for metrics collection."
    )
    args = parser.parse_args()

    try:
        # Initialize logging
        logger = await setup_logging(args.log_level, args.log_file)
        logger.info("Starting MCP Server...")

        # Initialize configuration
        config_dir = args.config_dir or os.getenv('MCP_CONFIG_DIR') or get_app_data_dir()
        config_dir_path = Path(config_dir).resolve()
        logger.info(f"Initializing ConfigManager with directory: {config_dir_path}")

        config_manager = ConfigManager(base_path=config_dir_path)
        await config_manager.initialize()

        # Create server instance
        server = await create_server_instance(config_manager, logger)

        # Initialize lifecycle manager
        lifecycle = ServerLifecycle(server, config_manager, logger)
        if not await lifecycle.initialize():
            raise RuntimeError("Server initialization failed")

        # Set up signal handlers
        setup_signal_handlers(lifecycle, logger)

        # Run server until shutdown
        await server.shutdown_event.wait()

    except Exception as e:
        if logger:
            logger.error(f"Server startup failed: {e}")
        else:
            print(f"Server startup failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if lifecycle:
            await lifecycle.cleanup()

async def create_server_instance(
    config_manager: ConfigManager,
    logger: logging.Logger
) -> MCPServer:
    """Create and initialize server instance."""
    try:
        initialized_components = await ServerInitializer.create_server(
            config=config_manager.current_config,
            logger=logger
        )
        optimizer, protocol_handler, capabilities = initialized_components

        server = MCPServer(
            config_manager.current_config,
            logger,
            protocol_handler,
            metrics_collector=initialized_components.get('metrics_collector')
        )
        server.optimizer = optimizer
        server.capabilities = capabilities

        # Initialize the server
        if not await server.initialize():
            raise RuntimeError("Server initialization failed")

        return server

    except Exception as e:
        logger.error(f"Failed to create server instance: {e}")
        raise

def setup_signal_handlers(lifecycle: ServerLifecycle, logger: logging.Logger):
    """Set up signal handlers for graceful shutdown."""
    if sys.platform == "win32":
        logger.warning("SIGHUP is not supported on Windows. Configuration reload is disabled.")
    else:
        loop = asyncio.get_running_loop()
        try:
            loop.add_signal_handler(
                signal.SIGHUP,
                lambda: asyncio.create_task(reload_config(
                    lifecycle.server,
                    lifecycle.config_manager,
                    logger
                ))
            )
        except NotImplementedError:
            logger.warning("Signal handling not implemented on this platform")

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(lifecycle.cleanup())
            )
            logger.debug(f"Signal handler for {sig.name} registered")
        except NotImplementedError:
            logger.warning(f"Signal handling for {sig.name} not implemented")

# Define missing functions
async def setup_logging(log_level: str, log_file: Optional[str]) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("MCPServer")
    logger.setLevel(log_level.upper())

    if log_file:
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_app_data_dir() -> str:
    """Get the application data directory."""
    home_dir = os.path.expanduser("~")
    app_data_dir = os.path.join(home_dir, ".mcp_server")
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    return app_data_dir

async def cleanup_sequence(server: MCPServer, logger: logging.Logger, config_manager: ConfigManager):
    """Perform cleanup sequence."""
    logger.info("Starting cleanup sequence...")

    # Proper resource cleanup
    try:
        await server.shutdown()
    except Exception as e:
        logger.error(f"Error during server shutdown: {e}")

    # Component shutdown sequence
    try:
        await server.shutdown_components()
    except Exception as e:
        logger.error(f"Error during component shutdown: {e}")

    # File cleanup
    try:
        temp_dir = Path(tempfile.gettempdir())
        for file in temp_dir.glob("mcp_server_*"):
            file.unlink()
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")

    # Process state cleanup
    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except Exception as e:
        logger.error(f"Error during process state cleanup: {e}")

    logger.info("Cleanup sequence completed.")

# Define the HealthCheck class before it is used
class HealthCheck:
    """Health check implementation."""
    def __init__(self, server: MCPServer, logger: logging.Logger):
        self.server = server
        self.logger = logger

    async def perform_check(self):
        """Perform health check."""
        self.logger.info("Performing health check...")

        # Database connectivity checks
        try:
            db_connection = await self.server.db_connection_check()
            if not db_connection:
                self.logger.error("Database connectivity check failed")
            else:
                self.logger.info("Database connectivity check passed")
        except Exception as e:
            self.logger.error(f"Database connectivity check error: {e}")

        # Memory usage monitoring
        try:
            memory_info = psutil.virtual_memory()
            self.logger.info(f"Memory usage: {memory_info.percent}%")
            if memory_info.percent > 80:
                self.logger.warning("High memory usage detected")
        except Exception as e:
            self.logger.error(f"Memory usage monitoring error: {e}")

        # File systems checks
        try:
            disk_usage = psutil.disk_usage('/')
            self.logger.info(f"Disk usage: {disk_usage.percent}%")
            if disk_usage.percent > 80:
                self.logger.warning("High disk usage detected")
        except Exception as e:
            self.logger.error(f"File systems check error: {e}")

        # Component health validation
        try:
            component_health = await self.server.component_health_check()
            if not component_health:
                self.logger.error("Component health check failed")
            else:
                self.logger.info("Component health check passed")
        except Exception as e:
            self.logger.error(f"Component health validation error: {e}")

        self.logger.info("Health check completed.")

async def health_check_monitor(health_check: HealthCheck, logger: logging.Logger, interval: int):
    """Monitor health checks."""
    while True:
        await health_check.perform_check()
        await asyncio.sleep(interval)

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error in run_server: {e}", file=sys.stderr)
        sys.exit(1)
