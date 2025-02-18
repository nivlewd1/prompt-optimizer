"""
Enhanced Conversation Handler Implementation

Features:
- Real-time conversation optimization with streaming support
- Memory-efficient state management with size limits
- Circuit breaker pattern for high load protection
- Comprehensive metrics and health monitoring
- Proper rate limit integration and backpressure
- Enhanced cleanup and resource management
"""

import asyncio
import logging
import weakref
from typing import Dict, Any, Optional, AsyncIterator, List, Set, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import json
import sys
import psutil
from contextlib import asynccontextmanager

from .shared_types import (
    OptimizationStream,
    StrategyContext,
    ProcessingLevel,
    OptimizationError,
    OptimizationErrorType,
    ComponentState,
    OptimizationType,
    RateLimitState,
    MetricsData
)
from .interfaces import (
    ConversationHandlerInterface,
    RateLimiterInterface,
    OptimizerInterface,
    TransportInterface,
    MetricsInterface
)

# Configuration constants
MAX_MESSAGES_PER_CONVERSATION = 100
MAX_OPTIMIZATION_HISTORY = 50
MEMORY_WARNING_THRESHOLD = 0.85  # 85% memory usage
MEMORY_CRITICAL_THRESHOLD = 0.95  # 95% memory usage
CLEANUP_INTERVAL = 300  # 5 minutes
METRICS_INTERVAL = 60   # 1 minute
MEMORY_CHECK_INTERVAL = 30  # 30 seconds
CONVERSATION_TIMEOUT = 1800  # 30 minutes
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_RESET_TIMEOUT = 60.0

@dataclass
class ConversationState:
    """Enhanced conversation state with memory management."""
    conversation_id: str
    component_state: ComponentState = field(default=ComponentState.UNINITIALIZED)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    optimization_types: Set[OptimizationType] = field(default_factory=set)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    metrics: MetricsData = field(default_factory=MetricsData)
    metadata: Dict[str, Any] = field(default_factory=dict)
    _optimization_results: Dict[str, Any] = field(default_factory=weakref.WeakValueDictionary)

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)

    def add_message(self, message: Dict[str, Any]):
        """Add message with size limit enforcement."""
        self.messages.append(message)
        self.update_activity()
        self._enforce_size_limits()
        self._update_message_metrics(message)

    def record_optimization(self, optimization: Dict[str, Any]):
        """Record optimization with memory-efficient storage."""
        result_id = str(len(self.optimization_history))
        self._optimization_results[result_id] = optimization.get('result')
        
        optimization_record = {
            'id': result_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'confidence_score': optimization.get('confidence_score'),
            'type': optimization.get('type'),
            'metadata': optimization.get('metadata', {})
        }
        
        self.optimization_history.append(optimization_record)
        if 'type' in optimization:
            self.optimization_types.add(optimization['type'])
        
        self._enforce_size_limits()
        self._update_optimization_metrics(optimization)

    def _enforce_size_limits(self):
        """Enforce size limits for messages and optimization history."""
        while len(self.messages) > MAX_MESSAGES_PER_CONVERSATION:
            self.messages.pop(0)
            
        while len(self.optimization_history) > MAX_OPTIMIZATION_HISTORY:
            oldest = self.optimization_history.pop(0)
            self._optimization_results.pop(oldest['id'], None)

    def _update_message_metrics(self, message: Dict[str, Any]):
        """Update metrics for new message."""
        metrics = self.metrics
        metrics.message_counts['total_messages'] += 1
        
        total_messages = metrics.message_counts['total_messages']
        metrics.resource_usage['avg_message_length'] = (
            (metrics.resource_usage.get('avg_message_length', 0) * 
             (total_messages - 1) +
             len(message.get('content', ''))) / total_messages
        )

    def _update_optimization_metrics(self, optimization: Dict[str, Any]):
        """Update metrics with memory-efficient storage."""
        metrics = self.metrics
        metrics.message_counts['total_optimizations'] += 1
        
        total_optimizations = metrics.message_counts['total_optimizations']
        
        if 'timing' in optimization:
            metrics.resource_usage['avg_optimization_time'] = (
                (metrics.resource_usage.get('avg_optimization_time', 0) * 
                 (total_optimizations - 1) +
                 optimization['timing']) / total_optimizations
            )
        
        if 'confidence_score' in optimization:
            metrics.resource_usage['avg_confidence'] = (
                (metrics.resource_usage.get('avg_confidence', 0) * 
                 (total_optimizations - 1) +
                 optimization['confidence_score']) / total_optimizations
            )

    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if conversation has expired."""
        return (
            not self.active or
            (datetime.now(timezone.utc) - self.last_activity).total_seconds() > timeout_seconds
        )

class CircuitBreaker:
    """Circuit breaker for handling high load scenarios."""
    
    def __init__(
        self,
        failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD,
        reset_timeout: float = CIRCUIT_BREAKER_RESET_TIMEOUT
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
        self.state = "closed"  # closed, open, half-open

    async def record_failure(self):
        """Record a failure occurrence."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"

    async def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        async with self._lock:
            if self.state == "open":
                if self.last_failure_time and (
                    datetime.now(timezone.utc) - self.last_failure_time
                ).total_seconds() > self.reset_timeout:
                    self.state = "half-open"
                    return False
                return True
            return False

    async def record_success(self):
        """Record a successful operation."""
        async with self._lock:
            if self.state == "half-open":
                self.state = "closed"
            self.failure_count = 0
            self.last_failure_time = None

class ConversationHandler(ConversationHandlerInterface):
    """Enhanced conversation handler with memory optimization and monitoring."""
    
    def __init__(
        self,
        optimizer: OptimizerInterface,
        config: Optional[Dict[str, Any]] = None,
        metrics_collector: Optional[MetricsInterface] = None
    ):
        """Initialize conversation handler with dependencies."""
        # Validate dependencies
        if not isinstance(optimizer, OptimizerInterface):
            raise TypeError("optimizer must implement OptimizerInterface")

        self.optimizer = optimizer
        self.config = config or {}
        self.logger = logging.getLogger("conversation-handler")
        self.metrics_collector = metrics_collector
        
        # State management
        self.conversations: Dict[str, ConversationState] = {}
        self.component_state = ComponentState.UNINITIALIZED
        self._conversation_lock = asyncio.Lock()
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        self._memory_monitor_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.conversation_timeout = self.config.get('conversation_timeout', CONVERSATION_TIMEOUT)
        self.cleanup_interval = self.config.get('cleanup_interval', CLEANUP_INTERVAL)
        self.metrics_interval = self.config.get('metrics_interval', METRICS_INTERVAL)
        self.memory_check_interval = self.config.get('memory_check_interval', MEMORY_CHECK_INTERVAL)

        # Metrics
        self.metrics = {
            "total_conversations": 0,
            "active_conversations": 0,
            "total_optimizations": 0,
            "active_optimizations": 0,
            "rate_limited_requests": 0,
            "avg_response_time": 0.0,
            "memory_usage": 0.0,
            "circuit_breaker_trips": 0
        }

    async def initialize(self) -> bool:
        """Initialize handler with memory monitoring."""
        try:
            self.component_state = ComponentState.INITIALIZING
            
            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())
            self._memory_monitor_task = asyncio.create_task(self._monitor_memory())
            
            self.component_state = ComponentState.READY
            self.logger.info("Conversation handler initialized successfully")
            return True
            
        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def _monitor_memory(self):
        """Monitor system memory usage."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(self.memory_check_interval)
                
                process = psutil.Process()
                memory_percent = process.memory_percent()
                self.metrics["memory_usage"] = memory_percent
                
                if memory_percent > MEMORY_CRITICAL_THRESHOLD:
                    self.logger.warning("Critical memory usage detected")
                    await self._handle_critical_memory()
                elif memory_percent > MEMORY_WARNING_THRESHOLD:
                    self.logger.warning("High memory usage detected")
                    await self._handle_high_memory()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")

    async def _handle_critical_memory(self):
        """Handle critical memory usage."""
        async with self._conversation_lock:
            # Force cleanup inactive conversations
            for conv_id, conv in list(self.conversations.items()):
                if not conv.active or (
                    datetime.now(timezone.utc) - conv.last_activity
                ).total_seconds() > 300:
                    await self.cleanup_conversation(conv_id)
            
            # Clear optimization history
            for conv in self.conversations.values():
                conv.optimization_history.clear()
                conv._optimization_results.clear()

    async def _handle_high_memory(self):
        """Handle high memory usage."""
        async with self._conversation_lock:
            # Reduce optimization history
            for conv in self.conversations.values():
                while len(conv.optimization_history) > MAX_OPTIMIZATION_HISTORY // 2:
                    oldest = conv.optimization_history.pop(0)
                    conv._optimization_results.pop(oldest['id'], None)

    @asynccontextmanager
    async def _conversation_operation(self, conversation_id: str):
        """Context manager for conversation operations with circuit breaker."""
        if await self.circuit_breaker.is_open():
            self.metrics["circuit_breaker_trips"] += 1
            raise OptimizationError(
                "Service temporarily unavailable",
                OptimizationErrorType.PROCESSING_ERROR
            )
            
        try:
            yield
            await self.circuit_breaker.record_success()
        except Exception as e:
            await self.circuit_breaker.record_failure()
            raise

    async def process_message(
        self,
        message: Dict[str, Any],
        conversation_id: str
    ) -> AsyncIterator[OptimizationStream]:
        """Process and optimize message with memory optimization."""
        start_time = datetime.now(timezone.utc)
        
        async with self._conversation_operation(conversation_id):
            try:
                # Get or create conversation state
                conversation = await self._get_or_create_conversation(conversation_id)
                
                # Add message
                conversation.add_message(message)
                
                # Prepare optimization request
                req = await self._prepare_optimization_request(message, conversation)
                
                # Process optimization
                async for result in self.optimizer.optimize_stream(req):
                    if result.complete:
                        await self._record_optimization_result(
                            conversation,
                            result,
                            start_time
                        )
                    
                    yield OptimizationStream(
                        interim_result=result.interim_result,
                        confidence_score=result.confidence_score,
                        complete=result.complete,
                        metadata={
                            "conversation_id": conversation_id,
                            "message_index": len(conversation.messages) - 1,
                            "optimization_type": "real-time",
                            "processing_time": (
                                datetime.now(timezone.utc) - start_time
                            ).total_seconds(),
                            **result.metadata
                        }
                    )
                    
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")
                self.metrics["active_optimizations"] -= 1
                if self.metrics_collector:
                    await self.metrics_collector.record_error(
                        "PROCESS_MESSAGE",
                        "conversation_handler",
                         e,
                        {"conversation_id": conversation_id}
                    )
                raise OptimizationError(
                    str(e),
                    OptimizationErrorType.PROCESSING_ERROR
                )

    async def _get_or_create_conversation(
        self,
        conversation_id: str
    ) -> ConversationState:
        """Get existing conversation or create new one."""
        async with self._conversation_lock:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = ConversationState(
                    conversation_id=conversation_id
                )
                self.metrics["total_conversations"] += 1
                self.metrics["active_conversations"] += 1
                
            return self.conversations[conversation_id]

    async def _prepare_optimization_request(
        self,
        message: Dict[str, Any],
        conversation: ConversationState
    ) -> Dict[str, Any]:
        """Prepare optimization request with context."""
        return {
            "base_prompt": message["content"],
            "optimization_goals": await self._derive_optimization_goals(conversation),
            "context": {
                "conversation_history": conversation.messages[-5:],
                "interaction_patterns": await self._analyze_interaction_patterns(conversation),
                "domain": await self._detect_conversation_domain(conversation),
                "technical_level": await self._assess_technical_level(conversation)
            },
            "processing_level": ProcessingLevel.STANDARD,
            "stream": True
        }

    async def _derive_optimization_goals(
        self,
        conversation: ConversationState
    ) -> List[Dict[str, Any]]:
        """Derive optimization goals from conversation context."""
        messages = conversation.messages[-5:]
        goals = []
        
        if any("```" in msg.get("content", "") for msg in messages):
            goals.append({
                "type": OptimizationType.TECHNICAL_PRECISION,
                "weight": 1.0
            })
        
        if any("?" in msg.get("content", "") for msg in messages):
            goals.append({
                "type": OptimizationType.CLARITY,
                "weight": 1.0
            })
        
        goals.extend([
            {
                "type": OptimizationType.CONTEXTUAL_RELEVANCE,
                "weight": 1.0
            },
            {
                "type": OptimizationType.SEMANTIC_PRESERVATION,
                "weight": 1.0
            }
        ])
        
        return goals

    async def _analyze_interaction_patterns(
        self,
        conversation: ConversationState
    ) -> Dict[str, Any]:
        """Analyze conversation interaction patterns."""
        messages = conversation.messages
        return {
            "message_count": len(messages),
            "avg_message_length": sum(len(m.get("content", "")) for m in messages) / max(len(messages), 1),
            "question_ratio": sum(1 for m in messages if "?" in m.get("content", "")) / max(len(messages), 1),
            "code_blocks": sum(1 for m in messages if "```" in m.get("content", ""))
        }

    async def _detect_conversation_domain(
        self,
        conversation: ConversationState
    ) -> str:
        """Detect the primary domain of conversation."""
        content = " ".join(m.get("content", "") for m in conversation.messages)
        
        domains = {
            "technical": ["code", "function", "programming", "algorithm"],
            "analytical": ["analyze", "compare", "evaluate"],
            "creative": ["design", "create", "generate"],
            "explanatory": ["explain", "describe", "how", "why"]
        }
        
        domain_scores = {
            domain: sum(1 for kw in keywords if kw.lower() in content.lower())
            for domain, keywords in domains.items()
        }
        
        return max(domain_scores.items(), key=lambda x: x[1])[0]

    async def _assess_technical_level(
        self,
        conversation: ConversationState
    ) -> str:
        """Assess technical level of conversation."""
        content = " ".join(m.get("content", "") for m in conversation.messages)
        
        technical_indicators = {
            "basic": ["help", "what is", "how do I"],
            "intermediate": ["implement", "optimize", "design pattern"],
            "advanced": ["complexity", "architecture", "scalability"]
        }
        
        scores = {
            level: sum(1 for ind in indicators if ind.lower() in content.lower())
            for level, indicators in technical_indicators.items()
        }
        
        return max(scores.items(), key=lambda x: x[1])[0]

    async def _record_optimization_result(
        self,
        conversation: ConversationState,
        result: OptimizationStream,
        start_time: datetime
    ):
        """Record optimization result with timing information."""
        optimization_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        optimization_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence_score": result.confidence_score,
            "timing": optimization_time,
            "type": result.metadata.get("optimization_type"),
            "metadata": result.metadata,
            "result": result.interim_result
        }
        
        conversation.record_optimization(optimization_record)
        self.metrics["avg_response_time"] = (
            (self.metrics["avg_response_time"] * self.metrics["total_optimizations"] +
             optimization_time) / (self.metrics["total_optimizations"] + 1)
        )

    async def _cleanup_loop(self):
        """Periodic cleanup of expired conversations."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                async with self._conversation_lock:
                    for conv_id, conv in list(self.conversations.items()):
                        if conv.is_expired(self.conversation_timeout):
                            await self.cleanup_conversation(conv_id)
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(1)

    async def _metrics_loop(self):
        """Periodic metrics collection and updates."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(self.metrics_interval)
                
                async with self._conversation_lock:
                    # Update active conversations count
                    self.metrics["active_conversations"] = len([
                        conv for conv in self.conversations.values()
                        if not conv.is_expired(self.conversation_timeout)
                    ])
                    
                    # Calculate aggregate metrics
                    total_messages = sum(
                        conv.metrics.message_counts.get("total_messages", 0)
                        for conv in self.conversations.values()
                    )
                    total_optimizations = sum(
                        conv.metrics.message_counts.get("total_optimizations", 0)
                        for conv in self.conversations.values()
                    )
                    
                    self.metrics.update({
                        "messages_per_conversation": (
                            total_messages / max(len(self.conversations), 1)
                        ),
                        "optimizations_per_conversation": (
                            total_optimizations / max(len(self.conversations), 1)
                        )
                    })
                
                if self.metrics_collector:
                     await self.metrics_collector.collect_metrics(self.metrics)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics loop: {e}")
                await asyncio.sleep(1)

    async def cleanup_conversation(self, conversation_id: str):
        """Cleanup conversation resources."""
        async with self._conversation_lock:
            if conversation_id in self.conversations:
                conversation = self.conversations[conversation_id]
                conversation.active = False
                
                if self.metrics["active_conversations"] > 0:
                    self.metrics["active_conversations"] -= 1
                
                del self.conversations[conversation_id]
                self.logger.info(f"Cleaned up conversation {conversation_id}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive conversation metrics."""
        async with self._conversation_lock:
            return {
                "conversations": {
                    "total": self.metrics["total_conversations"],
                    "active": self.metrics["active_conversations"],
                    "messages_per_conversation": self.metrics.get("messages_per_conversation", 0),
                    "optimizations_per_conversation": self.metrics.get("optimizations_per_conversation", 0)
                },
                "optimizations": {
                    "total": self.metrics["total_optimizations"],
                    "active": self.metrics["active_optimizations"],
                    "avg_response_time": self.metrics["avg_response_time"]
                },
                "system": {
                    "memory_usage": self.metrics["memory_usage"],
                    "circuit_breaker_trips": self.metrics["circuit_breaker_trips"]
                },
                "individual_conversations": {
                    conv_id: {
                        "messages": conv.metrics.message_counts.get("total_messages", 0),
                        "optimizations": conv.metrics.message_counts.get("total_optimizations", 0),
                        "avg_optimization_time": conv.metrics.resource_usage.get("avg_optimization_time", 0),
                        "avg_confidence": conv.metrics.resource_usage.get("avg_confidence", 0),
                        "active": conv.active,
                        "last_activity": conv.last_activity.isoformat()
                    }
                    for conv_id, conv in self.conversations.items()
                }
            }

    async def is_healthy(self) -> bool:
        """Check health of conversation handler."""
        try:
            if self.component_state != ComponentState.READY:
                return False
            
            if (not self._cleanup_task or 
                self._cleanup_task.done() or
                not self._metrics_task or 
                self._metrics_task.done() or
                not self._memory_monitor_task or
                self._memory_monitor_task.done()):
                return False
                
            if not hasattr(self, 'optimizer'):
                return False
            
            async with self._conversation_lock:
                pass
                
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self):
        """Cleanup handler resources."""
        self.logger.info("Starting conversation handler cleanup")
        
        try:
            self.component_state = ComponentState.SHUTTING_DOWN
            
            tasks = [self._cleanup_task, self._metrics_task, self._memory_monitor_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        self.logger.error(f"Error cancelling task: {e}")
            
            async with self._conversation_lock:
                for conv_id in list(self.conversations.keys()):
                    await self.cleanup_conversation(conv_id)
                self.conversations.clear()
            
            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Conversation handler cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            raise