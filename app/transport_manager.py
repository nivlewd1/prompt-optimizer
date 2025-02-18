"""
Enhanced Session Manager Implementation

Features:
- Complete session lifecycle management
- Enhanced security context handling
- Efficient database operations
- Comprehensive metrics collection
"""

import asyncio
import logging
import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Any, Optional, AsyncIterator, List, Union
from dataclasses import dataclass, field
from collections import defaultdict
import weakref
import aiosqlite

from .shared_types import (
    TransportType,
    ProtocolError,
    ErrorCodes,
    MCPVersion,
    ComponentState,
    SecurityContext,
    PROTOCOL_VERSION,
    MINIMAL_COMPATIBLE_VERSION,
    MessageStream,
    TransportMetrics
)
from .interfaces import (
    ServerInterface,
    SessionInterface,
    MetricsInterface,
    RateLimiterInterface
)

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

            # Persist# Persist final state
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

# Export for type checking
__all__ = ['SessionManager', 'SessionState']