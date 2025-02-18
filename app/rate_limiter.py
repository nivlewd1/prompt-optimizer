"""
Enhanced Rate Limiter Implementation

Features:
- Token bucket algorithm with size-aware consumption
- Adaptive rate limiting with backpressure
- Comprehensive metrics and state tracking
- Complete lifecycle management
- Enhanced memory optimization
- Testing support interfaces
- Full integration with connection and config components

Performance Targets:
- Token acquisition latency < 1ms
- Memory usage < 100MB for 10k clients
- Cleanup interval: 60s
- State transition latency < 0.1ms
"""

import asyncio
import logging
from typing import Dict, Set, Any, Optional, List, Union, Tuple, DefaultDict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from collections import defaultdict
import statistics
import time
import weakref
import psutil

from .shared_types import (
    RateLimitRule,
    RateLimitMetrics,
    RateLimitState,
    RateLimitConfig,
    ProtocolError,
    ErrorCodes,
    ComponentState,
    RateLimitError  # Import RateLimitError instead of RateLimitExceeded
)
from .interfaces import RateLimiterInterface

# --- Enhanced Rate Limit Types ---

@dataclass
class TokenBucketMetrics:
    """Enhanced metrics for token bucket performance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_wait_time: float = 0.0
    last_request_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    average_tokens_per_request: float = 0.0
    acquisition_times: List[float] = field(default_factory=list)
    size_distribution: DefaultDict[int, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def update_acquisition_time(self, time_ms: float) -> None:
        """Update token acquisition time metrics."""
        self.acquisition_times.append(time_ms)
        if len(self.acquisition_times) > 1000:  # Keep last 1000 samples
            self.acquisition_times = self.acquisition_times[-1000:]

    def get_acquisition_statistics(self) -> Dict[str, float]:
        """Get statistical analysis of acquisition times."""
        if not self.acquisition_times:
            return {
                "min_ms": 0.0,
                "max_ms": 0.0,
                "avg_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0
            }
        
        sorted_times = sorted(self.acquisition_times)
        return {
            "min_ms": min(sorted_times),
            "max_ms": max(sorted_times),
            "avg_ms": statistics.mean(sorted_times),
            "p95_ms": sorted_times[int(0.95 * len(sorted_times))],
            "p99_ms": sorted_times[int(0.99 * len(sorted_times))]
        }

@dataclass
class StateTransition:
    """Track state transitions with timing."""
    from_state: RateLimitState
    to_state: RateLimitState
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    reason: Optional[str] = None

    def complete(self) -> None:
        """Complete the transition with timing."""
        self.duration_ms = (
            datetime.now(timezone.utc) - self.timestamp
        ).total_seconds() * 1000

@dataclass
class TokenBucket:
    """Enhanced token bucket implementation."""
    rule: RateLimitRule
    tokens: float = field(init=False)
    last_update: float = field(init=False)
    state: RateLimitState = field(default=RateLimitState.NORMAL)
    state_history: List[StateTransition] = field(default_factory=list)
    blocked_until: Optional[datetime] = None
    consecutive_violations: int = 0
    last_state_change: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: TokenBucketMetrics = field(default_factory=TokenBucketMetrics)

    def __post_init__(self):
        self.tokens = float(self.rule.burst_size)
        self.last_update = time.monotonic()

    def update_tokens(self) -> None:
        """Add new tokens based on elapsed time."""
        if self.state == RateLimitState.BLOCKED:
            if datetime.now(timezone.utc) >= self.blocked_until:
                self._transition_state(RateLimitState.NORMAL, "Block period expired")
            else:
                return

        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(
            self.rule.burst_size,
            self.tokens + elapsed * self.rule.tokens_per_second
        )
        self.last_update = now
        self._update_state()

    def try_consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens from the bucket."""
        start_time = time.monotonic()
        
        if self.state == RateLimitState.BLOCKED:
            self.metrics.failed_requests += 1
            return False

        self.update_tokens()
        self.metrics.total_requests += 1
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            self.consecutive_violations = 0
            self.metrics.successful_requests += 1
            self.metrics.total_tokens_used += tokens
            self.metrics.update_acquisition_time(
                (time.monotonic() - start_time) * 1000
            )
            return True

        self.consecutive_violations += 1
        if self.consecutive_violations >= 5:  # Block after 5 consecutive violations
            self._transition_state(
                RateLimitState.BLOCKED,
                f"Blocked after {self.consecutive_violations} consecutive violations"
            )
            self.blocked_until = datetime.now(timezone.utc) + timedelta(minutes=5)

        self.metrics.failed_requests += 1
        return False

    def try_consume_for_size(self, size: int) -> bool:
        """Attempt to consume tokens based on content size."""
        required_tokens = max(1, size / 1024)  # 1 token per KB
        result = self.try_consume(int(required_tokens))
        if result:
            self.metrics.size_distribution[size] += 1
            self.metrics.average_tokens_per_request = (
                self.metrics.total_tokens_used / self.metrics.successful_requests
            )
        return result

    def _update_state(self) -> None:
        """Update bucket state based on current tokens."""
        new_state = None
        if self.state == RateLimitState.BLOCKED:
            return
        elif self.tokens == self.rule.burst_size:
            new_state = RateLimitState.NORMAL
        elif self.tokens > 0:
            new_state = RateLimitState.APPROACHING_LIMIT
        else:
            new_state = RateLimitState.LIMITED

        if new_state != self.state:
            self._transition_state(new_state, "Token level change")

    def _transition_state(self, new_state: RateLimitState, reason: str) -> None:
        """Record state transition with timing."""
        if new_state != self.state:
            transition = StateTransition(
                from_state=self.state,
                to_state=new_state,
                reason=reason
            )
            self.state = new_state
            self.last_state_change = datetime.now(timezone.utc)
            transition.complete()
            self.state_history.append(transition)
            
            # Keep only last 100 transitions
            if len(self.state_history) > 100:
                self.state_history = self.state_history[-100:]

    def get_state(self) -> Tuple[RateLimitState, Optional[datetime]]:
        """Get current state and block expiration if applicable."""
        self.update_tokens()
        return self.state, self.blocked_until if self.state == RateLimitState.BLOCKED else None

@dataclass
class RateLimiterMetrics:
    """Enhanced rate limiter system metrics."""
    total_buckets: int = 0
    active_buckets: int = 0
    total_requests: int = 0
    total_tokens: int = 0
    blocked_clients: int = 0
    memory_usage_mb: float = 0.0
    cleanup_count: int = 0
    last_cleanup: Optional[datetime] = None
    component_state: ComponentState = ComponentState.UNINITIALIZED
    error_count: int = 0

    def record_error(self) -> None:
        """Record an error occurrence."""
        self.error_count += 1

    def update_memory_usage(self) -> None:
        """Update memory usage metrics."""
        try:
            process = psutil.Process()
            self.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        except Exception:
            pass

class AdaptiveRateLimiter(RateLimiterInterface):
    """
    Enhanced rate limiter with adaptive limiting and comprehensive metrics.
    
    Features:
    - Dynamic token bucket management
    - Size-based rate limiting
    - Comprehensive metrics collection
    - Memory optimization
    - Testing interfaces
    """

    def __init__(
        self,
        config: Dict[str, Any],
        metrics_window: int = 3600  # 1 hour metrics window
    ):
        self.config = config
        self.logger = logging.getLogger("rate-limiter")
        
        # Initialize buckets with weak references for memory efficiency
        self.buckets: Dict[str, TokenBucket] = weakref.WeakValueDictionary()
        self.rules: Dict[str, RateLimitRule] = {}
        self._bucket_lock = asyncio.Lock()
        
        # Enhanced metrics
        self.metrics = RateLimiterMetrics()
        self.metrics_window = metrics_window
        
        # Component state
        self.component_state = ComponentState.UNINITIALIZED
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Initialize rate limiter with monitoring."""
        try:
            self.metrics.component_state = ComponentState.INITIALIZING
            
            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())
            
            self.metrics.component_state = ComponentState.READY
            self.component_state = ComponentState.READY
            self.logger.info("Rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.metrics.component_state = ComponentState.ERROR
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Rate limiter initialization failed: {e}")
            return False

    async def acquire(
        self,
        client_id: str,
        size: int = 0,
        wait: bool = True,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Acquire rate limit tokens for a client.
        
        Args:
            client_id: Client identifier
            size: Content size in bytes
            wait: Whether to wait if tokens aren't available
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if tokens were acquired
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        if self.component_state != ComponentState.READY:
            raise ProtocolError(
                "Rate limiter not initialized",
                ErrorCodes.SERVER_NOT_INITIALIZED
            )

        try:
            bucket = await self._get_bucket(client_id)
            start_time = time.monotonic()
            
            async with self._bucket_lock:
                state, blocked_until = bucket.get_state()
                if state == RateLimitState.BLOCKED:
                    retry_after = (blocked_until - datetime.now(timezone.utc)).total_seconds()
                    raise RateLimitError(
                        f"Client {client_id} is blocked",
                        client_id=client_id,
                        retry_after=retry_after
                    )

                # Try to consume tokens
                if bucket.try_consume_for_size(size):
                    acquisition_time = (time.monotonic() - start_time) * 1000
                    bucket.metrics.update_acquisition_time(acquisition_time)
                    return True

                if not wait:
                    raise RateLimitError(
                        f"Rate limit exceeded for client {client_id}",
                        client_id=client_id
                    )

                # Calculate wait time
                tokens_needed = max(1, size / 1024)
                wait_time = tokens_needed / bucket.rule.tokens_per_second

                if timeout is not None and wait_time > timeout:
                    raise RateLimitError(
                        f"Required wait time {wait_time:.2f}s exceeds timeout {timeout}s",
                        client_id=client_id,
                        retry_after=wait_time
                    )

                await asyncio.sleep(wait_time)
                
                if bucket.try_consume_for_size(size):
                    acquisition_time = (time.monotonic() - start_time) * 1000
                    bucket.metrics.update_acquisition_time(acquisition_time)
                    return True

                raise RateLimitError(
                    f"Rate limit exceeded after waiting {wait_time:.2f}s",
                    client_id=client_id,
                    retry_after=wait_time
                )

        except RateLimitError:
            raise
        except Exception as e:
            self.logger.error(f"Error acquiring rate limit: {e}")
            self.metrics.record_error()
            raise ProtocolError(
                "Rate limit error",
                ErrorCodes.INTERNAL_ERROR
            )

    async def _get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create a token bucket for a client."""
        async with self._bucket_lock:
            if client_id not in self.buckets:
                rule = self.rules.get(client_id, RateLimitRule(
                    tokens_per_second=self.config.get('tokens_per_second', 1.0),
                    burst_size=self.config.get('burst_size', 10),
                    window_seconds=self.config.get('window_seconds', 60.0)
                ))
                self.buckets[client_id] = TokenBucket(rule=rule)
                self.metrics.total_buckets += 1
                self.metrics.active_buckets += 1

            return self.buckets[client_id]

    async def get_state(self, client_id: str) -> RateLimitState:
        """Get the current rate limit state for a client."""
        async with self._bucket_lock:
            if client_id not in self.buckets:
                return RateLimitState.NORMAL
                
            state, _ = self.buckets[client_id].get_state()
            return state

    async def set_rule(self, client_id: str, rule: RateLimitConfig) -> None:
        """Set a custom rate limit rule for a client."""
        async with self._bucket_lock:
            new_rule = RateLimitRule(**rule.dict())
            self.rules[client_id] = new_rule
            if client_id in self.buckets:
                old_bucket = self.buckets[client_id]
                self.buckets[client_id] = TokenBucket(
                    rule=new_rule,
                    state=old_bucket.state,
                    blocked_until=old_bucket.blocked_until
                )

    async def _cleanup_loop(self) -> None:
        """Periodically cleanup old buckets and update metrics."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self._bucket_lock:
                    # Clean up buckets
                    now = datetime.now(timezone.utc)
                    cutoff = now - timedelta(seconds=self.metrics_window)
                    
                    for client_id, bucket in list(self.buckets.items()):
                        if bucket.metrics.last_request_time < cutoff:
                            del self.buckets[client_id]
                            self.metrics.active_buckets -= 1

                    # Update metrics
                    self.metrics.blocked_clients = sum(
                        1 for b in self.buckets.values()
                        if b.state == RateLimitState.BLOCKED
                    )
                    self.metrics.cleanup_count += 1
                    self.metrics.last_cleanup = now
                    self.metrics.update_memory_usage()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                self.metrics.record_error()

    async def _metrics_loop(self) -> None:
        """Collect and update metrics periodically."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                async with self._bucket_lock:
                    self.metrics.total_requests = sum(
                        b.metrics.total_requests
                        for b in self.buckets.values()
                    )
                    self.metrics.total_tokens = sum(
                        b.metrics.total_tokens_used
                        for b in self.buckets.values()
                    )
                    self.metrics.update_memory_usage()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics loop: {e}")
                self.metrics.record_error()

    async def get_metrics(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive rate limiting metrics."""
        async with self._bucket_lock:
            if client_id:
                if client_id not in self.buckets:
                    return {}
                    
                bucket = self.buckets[client_id]
                return {
                    "state": bucket.state.value,
                    "metrics": {
                        "total_requests": bucket.metrics.total_requests,
                        "successful_requests": bucket.metrics.successful_requests,
                        "failed_requests": bucket.metrics.failed_requests,
                        "total_tokens": bucket.metrics.total_tokens_used,
                        "average_tokens": bucket.metrics.average_tokens_per_request,
                        "acquisition_stats": bucket.metrics.get_acquisition_statistics(),
                        "size_distribution": dict(bucket.metrics.size_distribution)
                    },
                    "transitions": [
                        {
                            "from": t.from_state.value,
                            "to": t.to_state.value,
                            "timestamp": t.timestamp.isoformat(),
                            "duration_ms": t.duration_ms,
                            "reason": t.reason
                        }
                        for t in bucket.state_history[-10:]  # Last 10 transitions
                    ]
                }
            
            return {
                "system": {
                    "total_buckets": self.metrics.total_buckets,
                    "active_buckets": self.metrics.active_buckets,
                    "total_requests": self.metrics.total_requests,
                    "total_tokens": self.metrics.total_tokens,
                    "blocked_clients": self.metrics.blocked_clients,
                    "memory_usage_mb": self.metrics.memory_usage_mb,
                    "cleanup_stats": {
                        "count": self.metrics.cleanup_count,
                        "last_cleanup": (
                            self.metrics.last_cleanup.isoformat()
                            if self.metrics.last_cleanup else None
                        )
                    },
                    "error_count": self.metrics.error_count,
                    "component_state": self.metrics.component_state.value
                },
                "clients": {
                    client_id: {
                        "state": bucket.state.value,
                        "total_requests": bucket.metrics.total_requests,
                        "success_rate": (
                            bucket.metrics.successful_requests /
                            max(1, bucket.metrics.total_requests)
                        )
                    }
                    for client_id, bucket in self.buckets.items()
                }
            }

    @asynccontextmanager
    async def rate_limit_context(
        self,
        client_id: str,
        size: int = 0,
        wait: bool = True,
        timeout: Optional[float] = None
    ):
        """Context manager for rate limiting a block of code."""
        try:
            await self.acquire(client_id, size, wait, timeout)
            yield
        finally:
            # Update metrics on exit
            if client_id in self.buckets:
                bucket = self.buckets[client_id]
                bucket.metrics.last_request_time = datetime.now(timezone.utc)

    async def cleanup(self) -> None:
        """Cleanup rate limiter resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN
            self.metrics.component_state = ComponentState.SHUTTING_DOWN
            
            # Cancel background tasks
            for task in [self._cleanup_task, self._metrics_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Clear collections
            async with self._bucket_lock:
                self.buckets.clear()
                self.rules.clear()
            
            self.component_state = ComponentState.UNINITIALIZED
            self.metrics.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Rate limiter cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.metrics.record_error()
            self.component_state = ComponentState.ERROR
            self.metrics.component_state = ComponentState.ERROR
            raise

    async def is_healthy(self) -> bool:
        """Check rate limiter health status."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            # Check background tasks
            if any(
                task and task.done()
                for task in [self._cleanup_task, self._metrics_task]
            ):
                return False

            # Check memory usage
            self.metrics.update_memory_usage()
            if self.metrics.memory_usage_mb > 1024:  # 1GB limit
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False