import asyncio
import logging
from typing import Dict, Any, Optional, AsyncIterator, List
from datetime import datetime, timezone
import json
import weakref
import psutil
from dataclasses import dataclass, field
import dspy
from dspy.teleprompt import BootstrapFewShot

from .shared_types import (
    OptimizationType,
    ProcessingLevel,
    ValidationLevel,
    OptimizationError,
    OptimizationErrorType,
    DSPyConfig,
    OptimizationStream,
    ComponentState,
    MetricsData,
    StrategyContext
)
from .models import PromptOptimizationRequest
from .interfaces import (
    OptimizerInterface,
    RateLimiterInterface
)

# Constants for memory management
MAX_OPTIMIZATION_HISTORY = 1000
MEMORY_WARNING_THRESHOLD = 0.85
MEMORY_CRITICAL_THRESHOLD = 0.95
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_RESET_TIMEOUT = 60.0

class OptimizationPipeline(dspy.Module):
    """Enhanced DSPy pipeline for prompt optimization."""

    def __init__(self):
        """Initialize pipeline with advanced DSPy patterns."""
        super().__init__()
        try:
            self.teleprompter = BootstrapFewShot()

            # Enhanced predictors with chain-of-thought
            self.predict_approach = dspy.ChainOfThought(
                "prompt, goals, context -> strategy, enhanced_prompt, reasoning"
            )

            # Validation with confidence scoring
            self.validate_result = dspy.ChainOfThought(
                "original, enhanced, goals -> score, feedback, confidence"
            )

            # Context-aware refinement
            self.refine_with_context = dspy.ChainOfThought(
                "prompt, context, strategy -> refined_prompt, reasoning, adjustments"
            )

        except Exception as e:
            logging.error(f"Failed to initialize DSPy pipeline: {str(e)}", exc_info=True)
            raise OptimizationError(
                f"Failed to initialize DSPy pipeline: {str(e)}",
                OptimizationErrorType.STRATEGY_FAILURE
            )

    async def forward(
        self,
        prompt: str,
        goals: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> dspy.Prediction:
        """Execute forward pass through enhanced optimization pipeline."""
        try:
            # Initial prediction with context
            prediction = await self.predict_approach(
                prompt=prompt,
                goals=goals,
                context=json.dumps(context) if context else "{}"
            )

            # Apply context refinement if available
            if context:
                refinement = await self.refine_with_context(
                    prompt=prediction.enhanced_prompt,
                    context=json.dumps(context),
                    strategy=prediction.strategy
                )
                enhanced_prompt = refinement.refined_prompt
                reasoning = f"{prediction.reasoning}\nRefinements: {refinement.adjustments}"
            else:
                enhanced_prompt = prediction.enhanced_prompt
                reasoning = prediction.reasoning

            # Comprehensive validation
            validation = await self.validate_result(
                original=prompt,
                enhanced=enhanced_prompt,
                goals=goals
            )

            return dspy.Prediction(
                strategy=prediction.strategy,
                enhanced_prompt=enhanced_prompt,
                score=float(validation.score),
                confidence=float(validation.confidence),
                feedback=validation.feedback,
                reasoning=reasoning
            )

        except Exception as e:
            logging.error(f"Error in optimization pipeline: {str(e)}", exc_info=True)
            raise OptimizationError(
                f"Pipeline execution failed: {str(e)}",
                OptimizationErrorType.STRATEGY_FAILURE
            )

class CircuitBreaker:
    """Circuit breaker for handling optimization failures."""

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

@dataclass
class OptimizationCache:
    """Memory-efficient optimization cache."""
    results: Dict[str, Any] = field(default_factory=weakref.WeakValueDictionary)
    metrics: Dict[str, float] = field(default_factory=dict)
    max_size: int = MAX_OPTIMIZATION_HISTORY

    def add_result(self, key: str, result: Any, confidence: float):
        """Add result to cache with size management."""
        if len(self.results) >= self.max_size:
            oldest_key = next(iter(self.results))
            self.results.pop(oldest_key)
            self.metrics.pop(oldest_key, None)

        self.results[key] = result
        self.metrics[key] = confidence

    def get_result(self, key: str) -> Optional[tuple[Any, float]]:
        """Get result and confidence from cache."""
        result = self.results.get(key)
        confidence = self.metrics.get(key)
        if result is not None and confidence is not None:
            return result, confidence
        return None

class EnhancedPromptOptimizer(OptimizerInterface):
    """Enhanced prompt optimizer with comprehensive optimization capabilities."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        dspy_config: Optional[DSPyConfig] = None,
        rate_limiter: Optional[RateLimiterInterface] = None
    ):
        """Initialize optimizer with dependencies."""
        self.config = config or {}
        self.dspy_config = dspy_config or DSPyConfig()
        self.rate_limiter = rate_limiter
        self.logger = logging.getLogger("prompt-optimizer")

        try:
            # Initialize DSPy
            self.lm = dspy.OpenAI(
                model=self.dspy_config.model_name,
                temperature=self.dspy_config.temperature
            )
            dspy.settings.configure(lm=self.lm)

            # Initialize optimization pipeline
            self.pipeline = OptimizationPipeline()

            # Initialize circuit breaker
            self.circuit_breaker = CircuitBreaker()

            # Initialize cache
            self.cache = OptimizationCache()

            # Component state
            self.component_state = ComponentState.UNINITIALIZED

            # Metrics tracking
            self.metrics = MetricsData()

            # Memory monitoring
            self._memory_monitor_task: Optional[asyncio.Task] = None

        except Exception as e:
            self.logger.error(f"Optimizer initialization failed: {e}", exc_info=True)
            raise OptimizationError(
                f"Initialization failed: {str(e)}",
                OptimizationErrorType.STRATEGY_FAILURE
            )

    async def initialize(self) -> bool:
        """Initialize optimizer and monitoring."""
        try:
            self.component_state = ComponentState.INITIALIZING

            # Start memory monitoring
            self._memory_monitor_task = asyncio.create_task(self._monitor_memory())

            self.component_state = ComponentState.READY
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            return False

    async def optimize_stream(
        self,
        request: Dict[str, Any]
    ) -> AsyncIterator[OptimizationStream]:
        """Optimize prompt with streaming results."""
        start_time = datetime.now(timezone.utc)
        optimization_state = None

        try:
            # Rate limit check
            if self.rate_limiter:
                await self.rate_limiter.acquire(
                    client_id=request.get("client_id", "default"),
                    size=len(str(request))
                )

            # Check circuit breaker
            if await self.circuit_breaker.is_open():
                raise OptimizationError(
                    "Service temporarily unavailable",
                    OptimizationErrorType.PROCESSING_ERROR
                )

            # Parse and validate request
            optimization_request = PromptOptimizationRequest(**request)

            # Check cache
            cache_key = self._generate_cache_key(
                optimization_request.base_prompt,
                optimization_request.optimization_goals
            )
            if cached := self.cache.get_result(cache_key):
                result, confidence = cached
                yield OptimizationStream(
                    interim_result=result,
                    confidence_score=confidence,
                    complete=True,
                    metadata={"cached": True}
                )
                return

            # Initialize optimization state
            optimization_state = OptimizationState(
                request_id=optimization_request.request_id,
                base_prompt=optimization_request.base_prompt,
                processing_level=optimization_request.processing_level,
                validation_level=ValidationLevel.STANDARD,
                start_time=datetime.now(timezone.utc)
            )

            # Prepare context
            context = None
            if optimization_request.context:
                context = StrategyContext(
                    processing_level=optimization_request.processing_level,
                    domain=optimization_request.context.domain,
                    technical_requirements=optimization_request.context.technical_requirements,
                    semantic_requirements=[]
                ).dict()

            # Execute pipeline
            pipeline_result = await self.pipeline.forward(
                prompt=optimization_request.base_prompt,
                goals=[g.type.value for g in optimization_request.optimization_goals],
                context=context
            )

            yield OptimizationStream(
                interim_result=pipeline_result.enhanced_prompt,
                confidence_score=float(pipeline_result.confidence),
                complete=True,
                metadata={
                    "strategy": pipeline_result.strategy,
                    "feedback": pipeline_result.feedback,
                    "reasoning": pipeline_result.reasoning
                }
            )

            # Cache successful result
            self.cache.add_result(
                cache_key,
                pipeline_result.enhanced_prompt,
                float(pipeline_result.confidence)
            )

            # Update metrics
            await self._record_metrics(success=True, start_time=start_time)
            await self.circuit_breaker.record_success()

        except Exception as e:
            self.logger.error(f"Optimization error: {e}", exc_info=True)
            await self._record_metrics(success=False, start_time=start_time)
            await self.circuit_breaker.record_failure()

            yield OptimizationStream(
                interim_result=request.get("base_prompt", ""),
                confidence_score=0.0,
                complete=True,
                metadata={
                    "error": str(e),
                    "latency": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
            )

            if isinstance(e, OptimizationError):
                raise
            raise OptimizationError(
                str(e),
                OptimizationErrorType.STRATEGY_FAILURE
            )

        finally:
            if optimization_state:
                await self._cleanup_state(optimization_state)

    async def _monitor_memory(self):
        """Monitor memory usage."""
        while self.component_state == ComponentState.READY:
            try:
                await asyncio.sleep(30)

                process = psutil.Process()
                memory_percent = process.memory_percent()

                if memory_percent > MEMORY_CRITICAL_THRESHOLD:
                    self.logger.warning("Critical memory usage detected")
                    self.cache.results.clear()
                    self.cache.metrics.clear()

                elif memory_percent > MEMORY_WARNING_THRESHOLD:
                    self.logger.warning("High memory usage detected")
                    while len(self.cache.results) > MAX_OPTIMIZATION_HISTORY // 2:
                        oldest_key = next(iter(self.cache.results))
                        self.cache.results.pop(oldest_key)
                        self.cache.metrics.pop(oldest_key, None)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}", exc_info=True)

    async def _record_metrics(
        self,
        success: bool,
        start_time: datetime
    ) -> None:
        """Record optimization metrics."""
        try:
            self.metrics.total_requests += 1
            if success:
                self.metrics.successful_optimizations += 1

            latency = (datetime.now(timezone.utc) - start_time).total_seconds()
            total_reqs = self.metrics.total_requests
            current_avg = self.metrics.average_latency
            self.metrics.average_latency = (
                (current_avg * (total_reqs - 1) + latency) / total_reqs
            )
            self.metrics.error_rate = (
                (total_reqs - self.metrics.successful_optimizations) / total_reqs
            )
        except Exception as e:
            self.logger.error(f"Metrics recording error: {e}", exc_info=True)

    def _generate_cache_key(
        self,
        prompt: str,
        goals: List[Any]
    ) -> str:
        """Generate cache key from prompt and goals."""
        goals_str = ",".join(sorted(g.type.value for g in goals))
        return f"{hash(prompt)}:{goals_str}"

    async def cleanup(self):
        """Cleanup optimizer resources."""
        self.logger.info("Starting optimizer cleanup")

        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Cancel memory monitoring
            if self._memory_monitor_task and not self._memory_monitor_task.done():
                self._memory_monitor_task.cancel()
                try:
                    await self._memory_monitor_task
                except asyncio.CancelledError:
                    pass

            # Close DSPy resources
            if self.lm:
                await self.lm.aclose()

            # Clear cache
            self.cache.results.clear()
            self.cache.metrics.clear()

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Optimizer cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}", exc_info=True)
            self.component_state = ComponentState.ERROR
            raise

    async def is_healthy(self) -> bool:
        """Check optimizer health."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            if not all([self.pipeline, self.lm, self.cache]):
                return False

            if await self.circuit_breaker.is_open():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return False
