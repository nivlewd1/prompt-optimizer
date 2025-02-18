import asyncio
import logging
from typing import Dict, Any, Optional, Set, List, Union, DefaultDict, Literal
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, model_validator
from collections import defaultdict
import re
import platform
import sys
import os
import uuid
import aiosqlite
import json

from .interfaces import (
    ServerInterface,
    SessionInterface,
    MetricsInterface,
    RateLimiterInterface
)

# --- Protocol Constants ---
PROTOCOL_VERSION = "2.0.0"
MINIMAL_COMPATIBLE_VERSION = "2.0.0"
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# === Core Enums ===
class TransportType(str, Enum):
    STDIO = "stdio"
    WEBSOCKET = "websocket"

class ErrorCodes(IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_NOT_INITIALIZED = -32002
    OPTIMIZATION_FAILED = -33001
    CAPABILITY_MISMATCH = -33003
    VERSION_MISMATCH = -33004
    RATE_LIMIT_EXCEEDED = -33005
    WINDOWS_ERROR = -33006

class ConnectionErrorType(str, Enum):
    TRANSPORT_ERROR = "transport_error"
    PROTOCOL_ERROR = "protocol_error"
    RESOURCE_ERROR = "resource_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    WINDOWS_ERROR = "windows_error"
    UNKNOWN_ERROR = "unknown_error"

class OptimizationErrorType(str, Enum):
    CONFIGURATION_ERROR = "configuration_error"
    PERFORMANCE_ERROR = "performance_error"
    RESOURCE_LIMIT_ERROR = "resource_limit_error"
    UNKNOWN_ERROR = "unknown_error"

class OptimizationType(str, Enum):
    CLARITY = "clarity"
    CONCISENESS = "conciseness"
    TECHNICAL_ACCURACY = "technical_accuracy"
    DOMAIN_SPECIFIC = "domain_specific"

class ProcessingLevel(str, Enum):
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PRIORITY = "priority"

class ValidationLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

class PatternCategory(str, Enum):
    ANALYSIS = "analysis"
    TECHNICAL = "technical"
    CLARIFICATION = "clarification"
    STRUCTURING = "structuring"
    SIMPLIFICATION = "simplification"

class StrategyPhase(str, Enum):
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    REFINEMENT = "refinement"
    VALIDATION = "validation"

class RateLimitState(str, Enum):
    NORMAL = "normal"
    APPROACHING_LIMIT = "approaching_limit"
    LIMITED = "limited"
    BLOCKED = "blocked"

# === Core Data Classes ===
@dataclass
class ErrorContext:
    error_type: ConnectionErrorType
    error_code: ErrorCodes
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recoverable: bool = False
    recovery_attempts: int = 0
    windows_error_code: Optional[int] = None
    rate_limit_details: Optional[Dict[str, Any]] = None
    protocol_version: str = field(default=PROTOCOL_VERSION)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentState:
    name: str
    state: str
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_count: int = 0
    platform: str = field(default_factory=platform.system)
    metrics: Dict[str, Any] = field(default_factory=dict)
    rate_limit_state: RateLimitState = RateLimitState.NORMAL

# === Error Classes ===
class ProtocolError(Exception):
    def __init__(self, message: str, error_code: ErrorCodes):
        super().__init__(message)
        self.error_code = error_code

class OptimizationError(ProtocolError):
    def __init__(self, message: str, error_type: OptimizationErrorType):
        super().__init__(message, ErrorCodes.OPTIMIZATION_FAILED)
        self.error_type = error_type

class VersionError(ProtocolError):
    def __init__(self, message: str, current_version: 'MCPVersion', required_version: 'MCPVersion'):
        super().__init__(
            f"{message} (Current: {current_version.version}, Required: {required_version.version})",
            ErrorCodes.VERSION_MISMATCH
        )
        self.current_version = current_version
        self.required_version = required_version

class ConnectionError(Exception):
    def __init__(
        self,
        message: str,
        error_type: ConnectionErrorType,
        error_code: ErrorCodes,
        recoverable: bool = False,
        windows_error_code: Optional[int] = None,
        rate_limit_details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message)
        self.context = ErrorContext(
            error_type=error_type,
            error_code=error_code,
            recoverable=recoverable,
            windows_error_code=windows_error_code,
            rate_limit_details=rate_limit_details,
            details=kwargs
        )

# === Optimization Types ===
@dataclass
class OptimizationState:
    request_id: str
    base_prompt: str
    processing_level: ProcessingLevel
    validation_level: ValidationLevel
    start_time: datetime
    current_step: int = 0
    metrics: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    complete: bool = False

@dataclass
class PatternResult:
    pattern_id: str
    match_score: float
    matched_sections: List[Tuple[int, int]]
    suggested_improvements: List[str]
    confidence: float = 1.0

@dataclass
class StrategyResult:
    phase: StrategyPhase
    confidence_score: float
    interim_result: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

# === Configuration Classes ===
class DSPyConfig(BaseModel):
    model_name: str = Field(default="gpt-3.5-turbo", pattern=r"^gpt-(3\.5-turbo|4)")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_retries: int = Field(default=3, gt=0)
    timeout: float = Field(default=30.0, gt=0)
    enable_chain_of_thought: bool = True
    validation_strictness: ValidationLevel = ValidationLevel.STANDARD
    context_window: int = Field(default=4096, description="Token limit for context")
    safety_filters: bool = True

    @model_validator(mode='after')
    def validate_model_config(cls, values):
        if values.model_name == "gpt-4" and values.context_window > 8192:
            raise ValueError("GPT-4 context window cannot exceed 8192 tokens")
        return values

# === Protocol Types ===
@dataclass
class SecurityContext:
    require_encryption: bool = True
    allowed_origins: List[str] = field(default_factory=list)
    auth_token: Optional[str] = None
    protocol_version: str = PROTOCOL_VERSION

@dataclass
class StreamingConfig:
    chunk_size: int = 1024
    buffer_size: int = 4096
    timeout: float = 30.0

@dataclass
class StreamState:
    active: bool = False
    last_activity: datetime = field(default_factory=datetime.now)
    bytes_processed: int = 0

@dataclass
class MetricsData:
    timestamp: datetime = field(default_factory=datetime.now)
    values: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyContext:
    processing_level: ProcessingLevel
    domain: Optional[str] = None
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    semantic_requirements: List[str] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    metrics: MetricsData = field(default_factory=MetricsData)

# === Version Handling ===
class MCPVersion:
    def __init__(self, version: str):
        if not VERSION_PATTERN.match(version):
            raise ConnectionError(
                message=f"Invalid version format: {version}",
                error_type=ConnectionErrorType.PROTOCOL_ERROR,
                error_code=ErrorCodes.VERSION_MISMATCH
            )
        parts = version.split('.')
        self.major, self.minor, self.patch = map(int, parts)
        self.version = version

    @classmethod
    def parse(cls, version: str) -> 'MCPVersion':
        try:
            return cls(version)
        except (ValueError, IndexError) as e:
            raise ConnectionError(
                message=f"Version parsing failed: {version}",
                error_type=ConnectionErrorType.PROTOCOL_ERROR,
                error_code=ErrorCodes.VERSION_MISMATCH
            ) from e

    def is_compatible(self, other: Union[str, 'MCPVersion']) -> bool:
        compare = other if isinstance(other, MCPVersion) else self.parse(other)
        return self.major == compare.major and self.minor >= compare.minor

# === Rate Limiting System ===
SIZE_CATEGORIES = {
    "SMALL": 5000,
    "MEDIUM": 10000,
    "LARGE": 50000
}

class RateLimitConfig(BaseModel):
    tokens_per_second: float = Field(gt=0)
    burst_size: int = Field(gt=0)
    window_seconds: float = Field(gt=0)
    window_multiplier: float = Field(default=1.5, ge=1.0, le=5.0)
    size_thresholds: Dict[int, int] = Field(
        default_factory=lambda: {v: k+1 for k, v in enumerate(SIZE_CATEGORIES.values())}
    )

@dataclass
class RateLimitMetrics:
    interval_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interval_end: Optional[datetime] = None
    rate_limited_count: int = 0
    total_tokens_used: int = 0
    rate_limit_wait_time: float = 0.0
    size_distribution: DefaultDict[Literal["SMALL", "MEDIUM", "LARGE", "VERY_LARGE"], int] = field(
        default_factory=lambda: defaultdict(int)
    )
    platform: str = field(default_factory=platform.system)

class RateLimitError(ConnectionError):
    def __init__(self, message: str, client_id: str, retry_after: Optional[float] = None):
        super().__init__(
            message=message,
            error_type=ConnectionErrorType.RATE_LIMIT_ERROR,
            error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
            rate_limit_details={
                "client_id": client_id,
                "retry_after": retry_after,
                "platform": platform.system(),
                "protocol_version": PROTOCOL_VERSION
            }
        )

# === Pattern System ===
@dataclass
class PatternMetadata:
    category: PatternCategory
    complexity_level: int
    typical_expansion_factor: float
    recommended_processing_level: ProcessingLevel
    version: str = PROTOCOL_VERSION
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# === Session Management ===
@dataclass
class SessionState:
    """Enhanced session state tracking."""
    session_id: str
    client_id: str
    transport_type: str
    transport_instance_id: Optional[str] = None
    capabilities: Dict[str, Any] = field(default_factory=dict)
    rate_limit_tokens: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = field(default=0)
    reconnect_count: int = field(default=0)
    state: Dict[str, Any] = field(default_factory=dict)
    security_context: Optional[SecurityContext] = None

    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if session has expired."""
        return (datetime.now(timezone.utc) - self.last_activity).total_seconds() > timeout_seconds

    def update_activity(self):
        """Update session activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1

class SessionManager(SessionInterface):
    """Enhanced session manager with transport awareness and improved maintainability."""

    def __init__(
        self,
        config: Dict[str, Any],
        logger: logging.Logger,
        server: ServerInterface,
        metrics_collector: Optional[MetricsInterface] = None,
        rate_limiter: Optional[RateLimiterInterface] = None
    ):
        """Initialize session manager."""
        self.config = config
        self.logger = logger

        if not isinstance(server, ServerInterface):
            raise TypeError("server must implement ServerInterface")
        self.server = server

        self.metrics_collector = metrics_collector
        self.rate_limiter = rate_limiter
        self.sessions: Dict[str, SessionState] = {}
        self.transport_sessions: Dict[str, Set[str]] = {}
        self._session_lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._transport_states: Dict[str, Dict[str, Any]] = {}

        # Initialize database path
        self.db_path = Path(self.config.get('session_db_path', 'sessions.db'))

        # Component state
        self.component_state = ComponentState.UNINITIALIZED

    async def initialize(self) -> bool:
        """Initialize session management system."""
        try:
            self.component_state = ComponentState.INITIALIZING

            # Initialize database
            await self._init_database()

            # Load persisted sessions
            await self._load_persisted_sessions()

            # Initialize transport states
            await self._init_transport_states()

            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            self.component_state = ComponentState.READY
            self.logger.info("Session manager initialized successfully")
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Failed to initialize session manager: {e}")
            return False

    async def _init_database(self) -> None:
        """Initialize session database with enhanced error handling."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        client_id TEXT NOT NULL,
                        transport_type TEXT NOT NULL,
                        transport_instance_id TEXT,
                        capabilities TEXT NOT NULL,
                        rate_limit_tokens REAL NOT NULL,
                        created_at TEXT NOT NULL,
                        last_activity TEXT NOT NULL,
                        message_count INTEGER NOT NULL,
                        reconnect_count INTEGER NOT NULL,
                        state TEXT NOT NULL,
                        security_context TEXT
                    )
                """)
                await db.commit()
                self.logger.debug("Session database initialized")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    async def _load_persisted_sessions(self) -> None:
        """Load persisted sessions from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM sessions") as cursor:
                    async for row in cursor:
                        try:
                            session = SessionState(
                                session_id=row[0],
                                client_id=row[1],
                                transport_type=row[2],
                                transport_instance_id=row[3],
                                capabilities=json.loads(row[4]),
                                rate_limit_tokens=row[5],
                                created_at=datetime.fromisoformat(row[6]),
                                last_activity=datetime.fromisoformat(row[7]),
                                message_count=row[8],
                                reconnect_count=row[9],
                                state=json.loads(row[10]),
                                security_context=SecurityContext(**json.loads(row[11])) if row[11] else None
                            )
                            self.sessions[session.session_id] = session
                            self.transport_sessions.setdefault(session.transport_type, set()).add(session.session_id)
                            self.logger.debug(f"Loaded session {session.session_id} from database.")
                        except Exception as e:
                            self.logger.error(f"Error loading session {row[0]}: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Error loading persisted sessions: {e}", exc_info=True)
            raise

    async def _init_transport_states(self) -> None:
        """Initialize transport session tracking."""
        try:
            for transport_type in [TransportType.STDIO.value, TransportType.WEBSOCKET.value]:
                self.transport_sessions.setdefault(transport_type, set())
                self._transport_states[transport_type] = {
                    'initialized': False,
                    'active_sessions': len(self.transport_sessions[transport_type])
                }
            self.logger.debug("Transport states initialized.")
        except Exception as e:
            self.logger.error(f"Error initializing transport states: {e}", exc_info=True)
            raise

    async def create_session(
        self,
        client_id: str,
        transport_type: str,
        transport_instance_id: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Optional[SessionState]:
        """Create new session with transport validation."""
        async with self._session_lock:
            try:
                # Validate transport type
                if transport_type not in [TransportType.STDIO.value, TransportType.WEBSOCKET.value]:
                    self.logger.error(f"Invalid transport type: {transport_type}")
                    return None

                # For STDIO, verify single session
                if transport_type == TransportType.STDIO.value:
                    existing_sessions = await self.get_active_sessions()
                    if any(s.transport_type == TransportType.STDIO.value for s in existing_sessions):
                        self.logger.warning("Multiple STDIO sessions not allowed")
                        return None

                session_id = str(uuid.uuid4())
                session = SessionState(
                    session_id=session_id,
                    client_id=client_id,
                    transport_type=transport_type,
                    transport_instance_id=transport_instance_id,
                    capabilities=capabilities or {}
                )

                self.sessions[session_id] = session
                self.transport_sessions.setdefault(transport_type, set()).add(session_id)

                # Persist session
                await self._persist_session(session)

                # Update metrics
                if self.metrics_collector:
                    await self.metrics_collector.collect_metrics({
                        "event": "session_created",
                        "transport_type": transport_type,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

                return session

            except Exception as e:
                self.logger.error(f"Session creation failed: {e}")
                return None

    async def validate_session_message(
        self,
        session_id: str,
        message: Dict[str, Any],
        transport_instance_id: Optional[str] = None
    ) -> bool:
        """Validate session message with transport verification."""
        try:
            session = await self.get_session(session_id, transport_instance_id)
            if not session:
                return False

            # Validate transport instance if provided
            if (transport_instance_id and
                session.transport_instance_id and
                transport_instance_id != session.transport_instance_id):
                return False

            # Update session state
            session.update_activity()
            await self._persist_session(session)

            return True

        except Exception as e:
            self.logger.error(f"Message validation failed: {e}")
            return False

    async def _persist_session(self, session: SessionState) -> None:
        """Persist session state to database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO sessions (
                        session_id, client_id, transport_type,
                        transport_instance_id, capabilities,
                        rate_limit_tokens, created_at, last_activity,
                        message_count, reconnect_count, state,
                        security_context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session.session_id,
                        session.client_id,
                        session.transport_type,
                        session.transport_instance_id,
                        json.dumps(session.capabilities),
                        session.rate_limit_tokens,
                        session.created_at.isoformat(),
                        session.last_activity.isoformat(),
                        session.message_count,
                        session.reconnect_count,
                        json.dumps(session.state),
                        json.dumps(session.security_context.__dict__)
                        if session.security_context else None
                    )
                )
                await db.commit()

        except Exception as e:
            self.logger.error(f"Failed to persist session {session.session_id}: {e}")
            raise

    async def get_active_sessions(self) -> List[SessionState]:
        """Get list of active sessions."""
        async with self._session_lock:
            timeout = self.config.get('session_timeout', 1800)
            return [
                session for session in self.sessions.values()
                if not session.is_expired(timeout)
            ]

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired sessions."""
        cleanup_interval = self.config.get('cleanup_interval', 300)

        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(cleanup_interval)

                async with self._session_lock:
                    # Get expired sessions
                    timeout = self.config.get('session_timeout', 1800)
                    expired_sessions = [
                        sess_id for sess_id, session in self.sessions.items()
                        if session.is_expired(timeout)
                    ]

                    # Clean up expired sessions
                    for sess_id in expired_sessions:
                        await self.remove_session(sess_id)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(1)

    async def remove_session(self, session_id: str) -> None:
        """Remove session with cleanup."""
        async with self._session_lock:
            try:
                if session_id in self.sessions:
                    session = self.sessions.pop(session_id)

                    # Clean up transport tracking
                    if session.transport_type in self.transport_sessions:
                        self.transport_sessions[session.transport_type].discard(session_id)

                    # Remove from database
                    await self._delete_persisted_session(session_id)

                    # Update metrics
                    if self.metrics_collector:
                        await self.metrics_collector.collect_metrics({
                            "event": "session_removed",
                            "transport_type": session.transport_type,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

                    self.logger.info(f"Removed session {session_id}")

            except Exception as e:
                self.logger.error(f"Session removal failed: {e}")
                raise

    async def _delete_persisted_session(self, session_id: str) -> None:
        """Delete persisted session from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                await db.commit()

        except Exception as e:
            self.logger.error(f"Error deleting session {session_id} from database: {e}")
            raise

    async def get_metrics(self) -> Dict[str, Any]:
        """Get session metrics."""
        try:
            active_sessions = await self.get_active_sessions()

            metrics = {
                "total_sessions": len(self.sessions),
                "active_sessions": len(active_sessions),
                "transport_metrics": {
                    t_type: len(sessions)
                    for t_type, sessions in self.transport_sessions.items()
                },
                "session_states": {
                    "active": len(active_sessions),
                    "expired": len(self.sessions) - len(active_sessions)
                },
                "component_state": self.component_state.value
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return {}

    async def cleanup(self) -> None:
        """Cleanup session manager resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Cancel cleanup task
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Persist final state
            async with self._session_lock:
                for session in self.sessions.values():
                    await self._persist_session(session)

                self.sessions.clear()
                self.transport_sessions.clear()

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Session manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            self.component_state = ComponentState.ERROR
            raise

    async def is_healthy(self) -> bool:
        """Check session manager health."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            # Verify database connection
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT 1") as cursor:
                    await cursor.fetchone()

            # Check cleanup task
            if not self._cleanup_task or self._cleanup_task.done():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

# === Export List ===
__all__ = [
    # Core
    "PROTOCOL_VERSION",

    # Enums
    "TransportType",
    "ErrorCodes",
    "ConnectionErrorType",
    "OptimizationErrorType",
    "OptimizationType",
    "ProcessingLevel",
    "ValidationLevel",
    "PatternCategory",
    "StrategyPhase",
    "RateLimitState",

    # Errors
    "ProtocolError",
    "OptimizationError",
    "VersionError",
    "ConnectionError",
    "RateLimitError",

    # Data Classes
    "ErrorContext",
    "ComponentState",
    "OptimizationState",
    "PatternResult",
    "StrategyResult",
    "SecurityContext",
    "StreamingConfig",
    "StreamState",
    "MetricsData",
    "StrategyContext",

    # Configuration
    "DSPyConfig",
    "RateLimitConfig",
    "RateLimitMetrics",

    # Version
    "MCPVersion",

    # Pattern System
    "PatternMetadata",

    # Session Management
    "SessionState",
    "SessionManager",

    # Constants
    "SIZE_CATEGORIES"
]
