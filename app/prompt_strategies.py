
"""
Enhanced Prompt Strategy Implementation

Features:
- Dynamic strategy coordination using DSPy
- Real-time strategy adaptation
- Comprehensive metrics collection
- Rate limit awareness
- Memory-efficient processing
- Full integration with updated prompt patterns
"""

from typing import Dict, List, Optional, Any, AsyncIterator, Union
from datetime import datetime, timezone
import asyncio
import logging
import json
from collections import defaultdict
import dspy
from dspy.teleprompt import BootstrapFewShot

from .shared_types import (
    PatternCategory,
    StrategyPhase,
    StrategyContext,
    StrategyResult,
    ProcessingLevel,
    OptimizationType,
    OptimizationError,
    OptimizationErrorType,
    DSPyConfig,
    OptimizationStream,
    ComponentState
)
from .prompt_patterns import EnhancedPromptPatterns
from .interfaces import StrategyInterface

class DSPyStrategyModule(dspy.Module):
    """Enhanced DSPy module for strategy coordination."""
    
    def __init__(self, config: Optional[DSPyConfig] = None):
        """Initialize strategy module with configuration."""
        super().__init__()
        
        # Core strategy predictor with chain-of-thought
        self.predict_strategy = dspy.Predict(
            "prompt, phase, constraints -> strategy, approach, reasoning"
        )
        
        # Context refinement with confidence
        self.refine_with_context = dspy.Predict(
            "prompt, context, strategy -> refined_prompt, confidence, adjustments"
        )
        
        # Strategy validation with feedback
        self.validate_strategy = dspy.Predict(
            "original, enhanced, strategy -> score, feedback, suggestions"
        )
        
        # Pattern selection optimizer
        self.pattern_selector = dspy.Predict(
            "prompt, requirements -> pattern_type, confidence, rationale"
        )

        # Teleprompter for strategy bootstrapping
        self.teleprompter = BootstrapFewShot()

    async def forward(
        self,
        prompt: str,
        phase: StrategyPhase,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> dspy.Prediction:
        """Execute strategy prediction with comprehensive processing."""
        try:
            # Initial strategy prediction
            prediction = await self.predict_strategy(
                prompt=prompt,
                phase=phase.value,
                constraints=json.dumps(constraints or {})
            )
            
            # Apply context refinement if available
            if context:
                refinement = await self.refine_with_context(
                    prompt=prompt,
                    context=json.dumps(context),
                    strategy=prediction.strategy
                )
                enhanced = refinement.refined_prompt
                confidence = float(refinement.confidence)
                reasoning = f"{prediction.reasoning}\nRefinements: {refinement.adjustments}"
            else:
                enhanced = prompt
                confidence = 1.0
                reasoning = prediction.reasoning
            
            # Validate result
            validation = await self.validate_strategy(
                original=prompt,
                enhanced=enhanced,
                strategy=prediction.strategy
            )
            
            return dspy.Prediction(
                enhanced=enhanced,
                strategy=prediction.strategy,
                approach=prediction.approach,
                confidence=confidence,
                score=float(validation.score),
                feedback=validation.feedback,
                reasoning=reasoning,
                suggestions=validation.suggestions
            )
            
        except Exception as e:
            raise OptimizationError(
                f"Strategy execution failed: {str(e)}",
                OptimizationErrorType.STRATEGY_FAILURE
            )

class StrategyExecutor:
    """Handles strategy execution and coordination."""

    def __init__(
        self,
        dspy_module: DSPyStrategyModule,
        patterns: EnhancedPromptPatterns,
        config: Optional[Dict[str, Any]] = None
    ):
        self.dspy_module = dspy_module
        self.patterns = patterns
        self.config = config or {}
        self.logger = logging.getLogger("strategy-executor")
        
        # Performance tracking
        self.execution_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "average_confidence": 0.0,
            "phase_timings": defaultdict(float),
            "strategy_effectiveness": {}
        }

    async def execute_strategy(
        self,
        prompt: str,
        phase: StrategyPhase,
        context: Optional[StrategyContext] = None
    ) -> AsyncIterator[OptimizationStream]:
        """Execute strategy with real-time optimization."""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get strategy prediction
            prediction = await self.dspy_module.forward(
                prompt=prompt,
                phase=phase,
                context=context.dict() if context else None
            )
            
            # Yield initial strategy selection
            yield OptimizationStream(
                interim_result=prediction.enhanced,
                confidence_score=prediction.confidence,
                complete=False,
                metadata={
                    "phase": phase.value,
                    "strategy": prediction.strategy,
                    "reasoning": prediction.reasoning
                }
            )
            
            # Select and apply appropriate pattern
            pattern_selection = await self.dspy_module.pattern_selector(
                prompt=prediction.enhanced,
                requirements=json.dumps({
                    "strategy": prediction.strategy,
                    "phase": phase.value
                })
            )
            
            # Apply selected pattern
            async for pattern_result in self.patterns.apply_pattern_stream(
                prediction.enhanced,
                PatternCategory(pattern_selection.pattern_type),
                context
            ):
                if pattern_result.complete:
                    # Update metrics
                    await self._update_metrics(
                        phase,
                        prediction.confidence,
                        pattern_result.confidence_score,
                        start_time
                    )
                
                yield OptimizationStream(
                    interim_result=pattern_result.interim_result,
                    confidence_score=min(
                        prediction.confidence,
                        pattern_result.confidence_score
                    ),
                    complete=pattern_result.complete,
                    metadata={
                        **pattern_result.metadata,
                        "strategy": prediction.strategy,
                        "suggestions": prediction.suggestions,
                        "total_time": (datetime.now() - start_time).total_seconds()
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Strategy execution error: {e}")
            raise OptimizationError(
                str(e),
                OptimizationErrorType.STRATEGY_FAILURE
            )

    async def _update_metrics(
        self,
        phase: StrategyPhase,
        strategy_confidence: float,
        pattern_confidence: float,
        start_time: datetime
    ):
        """Update execution metrics."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        self.execution_metrics["total_executions"] += 1
        self.execution_metrics["successful_executions"] += 1
        
        # Update confidence metrics
        total = self.execution_metrics["successful_executions"]
        current_avg = self.execution_metrics["average_confidence"]
        self.execution_metrics["average_confidence"] = (
            (current_avg * (total - 1) + min(strategy_confidence, pattern_confidence)) / total
        )
        
        # Update phase timing
        self.execution_metrics["phase_timings"][phase.value] = (
            (self.execution_metrics["phase_timings"][phase.value] * (total - 1) +
             execution_time) / total
        )
        
        # Update strategy effectiveness
        strategy_metrics = self.execution_metrics["strategy_effectiveness"]
        if phase.value not in strategy_metrics:
            strategy_metrics[phase.value] = {
                "total_uses": 0,
                "avg_confidence": 0.0,
                "avg_execution_time": 0.0
            }
        
        phase_metrics = strategy_metrics[phase.value]
        phase_metrics["total_uses"] += 1
        phase_metrics["avg_confidence"] = (
            (phase_metrics["avg_confidence"] * (phase_metrics["total_uses"] - 1) +
             min(strategy_confidence, pattern_confidence)) / phase_metrics["total_uses"]
        )
        phase_metrics["avg_execution_time"] = (
            (phase_metrics["avg_execution_time"] * (phase_metrics["total_uses"] - 1) +
             execution_time) / phase_metrics["total_uses"]
        )

class EnhancedOptimizationStrategies(StrategyInterface):
    """Enhanced strategy coordinator with DSPy integration."""
    
    def __init__(
        self,
        patterns: EnhancedPromptPatterns,
        dspy_config: Optional[DSPyConfig] = None
    ):
        """Initialize strategy coordinator."""
        self.patterns = patterns
        self.dspy_config = dspy_config or DSPyConfig()
        self.logger = logging.getLogger("prompt-strategies")
        
        # Initialize DSPy components
        self.lm = dspy.OpenAI(
            model=self.dspy_config.model_name,
            temperature=self.dspy_config.temperature
        )
        dspy.settings.configure(lm=self.lm)
        
        # Initialize strategy module
        self.strategy_module = DSPyStrategyModule(self.dspy_config)
        
        # Initialize executor
        self.executor = StrategyExecutor(
            dspy_module=self.strategy_module,
            patterns=self.patterns,
            config=self.dspy_config.dict()
        )
        
        # Component state
        self.component_state = ComponentState.UNINITIALIZED
        
        # Define optimization phases
        self.strategy_phases = {
            StrategyPhase.ANALYSIS: self._analysis_phase_stream,
            StrategyPhase.ENHANCEMENT: self._enhancement_phase_stream,
            StrategyPhase.REFINEMENT: self._refinement_phase_stream,
            StrategyPhase.VALIDATION: self._validation_phase_stream
        }

    async def initialize(self) -> bool:
        """Initialize strategy coordinator."""
        try:
            self.component_state = ComponentState.INITIALIZING
            
            # Verify patterns are initialized
            if not await self.patterns.is_healthy():
                self.logger.error("Pattern system not healthy")
                return False
            
            self.component_state = ComponentState.READY
            return True
            
        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def optimize_prompt_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute optimization strategy with streaming results."""
        if self.component_state != ComponentState.READY:
            raise OptimizationError(
                "Strategy coordinator not initialized",
                OptimizationErrorType.STRATEGY_FAILURE
            )

        start_time = datetime.now(timezone.utc)
        current_prompt = prompt
        current_confidence = 0.0
        phase_results = []
        
        try:
            # Execute each optimization phase
            for phase in StrategyPhase:
                if not self._should_apply_phase(phase, context.processing_level):
                    continue
                
                self.logger.info(f"Starting phase: {phase.value}")
                phase_start = datetime.now(timezone.utc)
                
                # Apply phase strategy
                async for result in self.strategy_phases[phase](
                    current_prompt,
                    context
                ):
                    current_prompt = result.interim_result
                    current_confidence = max(
                        current_confidence,
                        result.confidence_score
                    )
                    
                    if result.complete:
                        phase_results.append({
                            "phase": phase.value,
                            "confidence": result.confidence_score,
                            "duration": (
                                datetime.now(timezone.utc) - phase_start
                            ).total_seconds()
                        })
                    
                    yield OptimizationStream(
                        interim_result=current_prompt,
                        confidence_score=current_confidence,
                        complete=False,
                        metadata={
                            "phase": phase.value,
                            "processing_level": context.processing_level if context else None,
                            "phase_results": phase_results,
                            "current_phase": len(phase_results)
                        }
                    )
            
            # Final validation and metrics update
            final_score = await self._validate_optimization(
                original_prompt=prompt,
                enhanced_prompt=current_prompt,
                phase_results=phase_results
            )
            
            # Update executor metrics
            total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_strategy_metrics(phase_results, total_time, final_score)
            
            # Yield final result
            yield OptimizationStream(
                interim_result=current_prompt,
                confidence_score=final_score,
                complete=True,
                metadata={
                    "total_phases": len(phase_results),
                    "total_time": total_time,
                    "metrics": self.executor.execution_metrics
                }
            )
            
        except Exception as e:
            self.logger.error(f"Strategy error: {e}")
            
            # Return last successful result or original
            yield OptimizationStream(
                interim_result=current_prompt or prompt,
                confidence_score=current_confidence,
                complete=True,
                metadata={"error": str(e)}
            )

    async def _analysis_phase_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute analysis phase."""
        async for result in self.executor.execute_strategy(
            prompt=prompt,
            phase=StrategyPhase.ANALYSIS,
            context=context
        ):
            yield result

    async def _enhancement_phase_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute enhancement phase."""
        async for result in self.executor.execute_strategy(
            prompt=prompt,
            phase=StrategyPhase.ENHANCEMENT,
            context=context
        ):
            yield result

    async def _refinement_phase_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute refinement phase."""
        async for result in self.executor.execute_strategy(
            prompt=prompt,
            phase=StrategyPhase.REFINEMENT,
            context=context
        ):
            yield result

    async def _validation_phase_stream(
        self,
        prompt: str,
        context: Optional[StrategyContext]
    ) -> AsyncIterator[OptimizationStream]:
        """Execute validation phase."""
        async for result in self.executor.execute_strategy(
            prompt=prompt,
            phase=StrategyPhase.VALIDATION,
            context=context
        ):
            yield result

    def _should_apply_phase(
        self,
        phase: StrategyPhase,
        processing_level: Optional[ProcessingLevel]
    ) -> bool:
        """Determine if phase should be applied based on processing level."""
        if not processing_level:
            return True
            
        phase_requirements = {
            ProcessingLevel.MINIMAL: {
                StrategyPhase.ANALYSIS,
                StrategyPhase.VALIDATION
            },
            ProcessingLevel.STANDARD: {
                StrategyPhase.ANALYSIS,
                StrategyPhase.ENHANCEMENT,
                StrategyPhase.VALIDATION
            },
            ProcessingLevel.FULL: set(StrategyPhase)
        }
        
        return phase in phase_requirements.get(processing_level, set())

    async def _validate_optimization(
        self,
        original_prompt: str,
        enhanced_prompt: str,
        phase_results: List[Dict[str, Any]]
    ) -> float:
        """Validate complete optimization process."""
        try:
            validation = await self.strategy_module.validate_strategy(
                original=original_prompt,
                enhanced=enhanced_prompt,
                strategy="final_validation"
            )
            
            return float(validation.score)
        except:
            # Fallback to average confidence if validation fails
            return sum(r["confidence"] for r in phase_results) / len(phase_results)

    async def _update_strategy_metrics(
        self,
        phase_results: List[Dict[str, Any]],
        total_time: float,
        final_score: float
    ):
        """Update strategy coordinator metrics."""
        for phase_result in phase_results:
            phase = phase_result["phase"]
            confidence = phase_result["confidence"]
            duration = phase_result["duration"]
            
            self.executor.execution_metrics["phase_timings"][phase] = (
                (self.executor.execution_metrics["phase_timings"][phase] * 
                 self.executor.execution_metrics["total_executions"] +
                 duration) / (self.executor.execution_metrics["total_executions"] + 1)
            )
            
            strategy_metrics = self.executor.execution_metrics["strategy_effectiveness"]
            if phase not in strategy_metrics:
                strategy_metrics[phase] = {
                    "total_uses": 0,
                    "avg_confidence": 0.0,
                    "avg_execution_time": 0.0
                }
            
            phase_metrics = strategy_metrics[phase]
            phase_metrics["total_uses"] += 1
            phase_metrics["avg_confidence"] = (
                (phase_metrics["avg_confidence"] * (phase_metrics["total_uses"] - 1) +
                 confidence) / phase_metrics["total_uses"]
            )
            phase_metrics["avg_execution_time"] = (
                (phase_metrics["avg_execution_time"] * (phase_metrics["total_uses"] - 1) +
                 duration) / phase_metrics["total_uses"]
            )

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive strategy metrics."""
        return {
            "execution_metrics": self.executor.execution_metrics,
            "patterns": await self.patterns.get_metrics(),
            "component_state": self.component_state.value,
            "dspy_config": self.dspy_config.dict()
        }

    async def is_healthy(self) -> bool:
        """Check strategy coordinator health."""
        try:
            if self.component_state != ComponentState.READY:
                return False
            
            # Check patterns health
            if not await self.patterns.is_healthy():
                return False
            
            # Verify DSPy configuration
            if not self.dspy_config or not self.lm:
                return False
            
            # Check executor state
            if not hasattr(self, 'executor') or not self.executor:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self):
        """Cleanup strategy coordinator resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN
            
            # Close DSPy resources
            if self.lm:
                await self.lm.aclose()
            
            # Cleanup patterns
            await self.patterns.cleanup()
            
            # Clear metrics and state
            self.executor.execution_metrics.clear()
            
            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Strategy coordinator cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.component_state = ComponentState.ERROR
            raise