"""
Enhanced Prompt Pattern Implementation

Features:
- Improved DSPy integration for pattern optimization
- Enhanced pattern validation and verification
- Comprehensive metrics tracking
- Memory-efficient pattern application
- Proper cleanup procedures
"""

from typing import Dict, List, Optional, Any, AsyncIterator, Tuple
from datetime import datetime
import asyncio
import logging
import json
import dspy
from pydantic import BaseModel, Field

from .shared_types import (
    PatternCategory,
    StrategyContext,
    ProcessingLevel,
    ValidationLevel,
    PatternMetadata,
    PatternResult,
    OptimizationError,
    OptimizationErrorType,
    DSPyConfig,
    OptimizationStream,
    ComponentState
)
from .interfaces import PatternInterface

class PatternRegistry(BaseModel):
    """Registry for pattern definitions and metadata."""
    metadata: PatternMetadata
    structure: List[str]
    examples: Optional[List[str]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    dspy_config: Optional[DSPyConfig] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    last_validation: Optional[datetime] = None

    def apply(self, prompt: str, context: Optional[str] = None) -> str:
        """Apply pattern to prompt using enhanced templating."""
        try:
            template = self._format_structure(self.structure)

            # Enhanced context handling
            context_elements = []
            if context:
                context_elements.extend(self._parse_context(context))

            # Apply template with dynamic element ordering
            result = self._apply_template(prompt, template, context_elements)
            
            # Validate result before returning
            self._validate_result(result)
            
            return result

        except Exception as e:
            raise OptimizationError(
                f"Pattern application failed: {str(e)}",
                OptimizationErrorType.PATTERN_FAILURE
            )

    def _format_structure(self, structure: List[str]) -> str:
        """Format structure elements with enhanced readability."""
        formatted = []
        for idx, item in enumerate(structure):
            if idx > 0 and not item.startswith(('-', '*', '1.')):
                formatted.append('')  # Add spacing for readability
            formatted.append(f"- {item}")
        return "\n".join(formatted)

    def _parse_context(self, context: str) -> List[str]:
        """Parse and structure context elements."""
        elements = []
        ctx_lines = context.split('\n')
        current_section = None

        for line in ctx_lines:
            line = line.strip()
            if line.endswith(':'):
                current_section = line[:-1]
                elements.append(f"\n{current_section}:")
            elif line and current_section:
                elements.append(f"  - {line}")
            elif line:
                elements.append(line)

        return elements

    def _apply_template(
        self,
        prompt: str,
        template: str,
        context_elements: List[str]
    ) -> str:
        """Apply template with dynamic formatting."""
        sections = [
            "Task Content:",
            prompt,
            *context_elements,
            "\nResponse Structure:",
            template
        ]
        return "\n".join(s for s in sections if s)

    def _validate_result(self, result: str) -> None:
        """Validate generated result against rules."""
        if not result.strip():
            raise OptimizationError(
                "Empty result generated",
                OptimizationErrorType.PATTERN_FAILURE
            )
        
        if self.validation_rules:
            self._apply_validation_rules(result)

    def _apply_validation_rules(self, result: str) -> None:
        """Apply defined validation rules to result."""
        rules = self.validation_rules or {}
        
        # Length validation
        if 'min_length' in rules and len(result) < rules['min_length']:
            raise OptimizationError(
                f"Result too short: {len(result)} < {rules['min_length']}",
                OptimizationErrorType.PATTERN_FAILURE
            )
            
        # Structure validation
        if 'required_sections' in rules:
            missing = [
                section for section in rules['required_sections']
                if section not in result
            ]
            if missing:
                raise OptimizationError(
                    f"Missing required sections: {missing}",
                    OptimizationErrorType.PATTERN_FAILURE
                )

class DSPyPatternModule(dspy.Module):
    """Enhanced DSPy module for pattern-based optimization."""
    
    def __init__(self, config: Optional[DSPyConfig] = None):
        """Initialize pattern module with configuration."""
        super().__init__()
        
        # Pattern application predictor with enhanced signature
        self.pattern_predictor = dspy.Predict(
            "prompt, pattern_type, requirements -> enhanced, confidence, rationale"
        )
        
        # Context integration with explanation
        self.context_integration = dspy.Predict(
            "prompt, context -> integrated_prompt, reasoning, confidence"
        )
        
        # Enhanced validation predictor
        self.pattern_validator = dspy.Predict(
            "original, enhanced, requirements -> is_valid, score, feedback"
        )

    async def forward(
        self,
        prompt: str,
        pattern_type: str,
        context: Optional[Dict[str, Any]] = None,
        requirements: Optional[Dict[str, Any]] = None
    ) -> dspy.Prediction:
        """Apply pattern using enhanced DSPy pipeline."""
        try:
            # Initial pattern application with requirements
            prediction = await self.pattern_predictor(
                prompt=prompt,
                pattern_type=pattern_type,
                requirements=json.dumps(requirements or {})
            )
            
            # Context integration if provided
            if context:
                integration = await self.context_integration(
                    prompt=prediction.enhanced,
                    context=json.dumps(context)
                )
                enhanced = integration.integrated_prompt
                reasoning = integration.reasoning
                confidence = min(
                    float(prediction.confidence),
                    float(integration.confidence)
                )
            else:
                enhanced = prediction.enhanced
                reasoning = prediction.rationale
                confidence = float(prediction.confidence)
            
            # Comprehensive validation
            validation = await self.pattern_validator(
                original=prompt,
                enhanced=enhanced,
                requirements=json.dumps(requirements or {})
            )
            
            return dspy.Prediction(
                enhanced=enhanced,
                confidence=confidence,
                score=float(validation.score),
                reasoning=reasoning,
                feedback=validation.feedback
            )
            
        except Exception as e:
            raise OptimizationError(
                f"DSPy pattern application failed: {str(e)}",
                OptimizationErrorType.PATTERN_FAILURE
            )

class EnhancedPromptPatterns(PatternInterface):
    """Enhanced pattern collection with improved DSPy integration."""
    
    def __init__(self, dspy_config: Optional[DSPyConfig] = None):
        """Initialize pattern system."""
        self.logger = logging.getLogger("prompt-patterns")
        self.dspy_config = dspy_config or DSPyConfig()
        
        # Initialize DSPy components
        self.lm = dspy.OpenAI(
            model=self.dspy_config.model_name,
            temperature=self.dspy_config.temperature
        )
        dspy.settings.configure(lm=self.lm)
        
        # Initialize pattern module with config
        self.dspy_pattern = DSPyPatternModule(self.dspy_config)
        
        # Initialize registry and patterns
        self.pattern_registry = {}
        self._initialize_patterns()
        
        # Component state
        self.component_state = ComponentState.UNINITIALIZED
        
        # Enhanced metrics
        self.metrics = {
            "total_applications": 0,
            "successful_applications": 0,
            "average_confidence": 0.0,
            "pattern_usage": {},
            "performance_metrics": {
                "avg_application_time": 0.0,
                "avg_validation_time": 0.0
            },
            "validation_metrics": {
                "total_validations": 0,
                "failed_validations": 0
            }
        }

    async def initialize(self) -> bool:
        """Initialize pattern system."""
        try:
            self.component_state = ComponentState.INITIALIZING
            
            # Validate patterns
            validation_results = await self._validate_patterns()
            if not all(validation_results.values()):
                self.logger.error("Pattern validation failed")
                return False

            self.component_state = ComponentState.READY
            return True

        except Exception as e:
            self.component_state = ComponentState.ERROR
            self.logger.error(f"Initialization failed: {e}")
            return False

    async def _validate_patterns(self) -> Dict[str, bool]:
        """Validate all registered patterns."""
        results = {}
        for pattern_type, pattern in self.pattern_registry.items():
            try:
                # Validate structure
                if not pattern.structure:
                    results[pattern_type] = False
                    continue

                # Validate examples if provided
                if pattern.examples:
                    for example in pattern.examples:
                        try:
                            pattern.apply(example)
                        except Exception:
                            results[pattern_type] = False
                            break
                    else:
                        results[pattern_type] = True
                else:
                    results[pattern_type] = True

                # Update validation timestamp
                pattern.last_validation = datetime.now()

            except Exception as e:
                self.logger.error(f"Pattern validation error for {pattern_type}: {e}")
                results[pattern_type] = False

        return results

    async def apply_pattern_stream(
        self,
        prompt: str,
        pattern_type: PatternCategory,
        context: Optional[StrategyContext] = None
    ) -> AsyncIterator[OptimizationStream]:
        """Apply pattern with streaming results and enhanced monitoring."""
        start_time = datetime.now()

        try:
            # Validate pattern type
            if pattern_type not in self.pattern_registry:
                raise ValueError(f"Unknown pattern type: {pattern_type}")
            
            pattern = self.pattern_registry[pattern_type]
            
            # Initial template-based result
            template_result = pattern.apply(
                prompt,
                self._build_context_elements(context) if context else None
            )
            
            yield OptimizationStream(
                interim_result=template_result,
                confidence_score=0.7,
                complete=False,
                metadata={
                    "method": "template",
                    "pattern_type": pattern_type.value,
                    "generation_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
            # Prepare requirements for DSPy
            requirements = self._prepare_requirements(pattern, context)
            
            # Apply DSPy enhancement
            prediction = await self.dspy_pattern.forward(
                prompt=template_result,
                pattern_type=pattern_type.value,
                context=context.dict() if context else None,
                requirements=requirements
            )
            
            # Update metrics
            await self._update_metrics(
                pattern_type,
                float(prediction.confidence),
                start_time
            )
            
            yield OptimizationStream(
                interim_result=prediction.enhanced,
                confidence_score=float(prediction.confidence),
                complete=True,
                metadata={
                    "method": "dspy",
                    "pattern_type": pattern_type.value,
                    "reasoning": prediction.reasoning,
                    "feedback": prediction.feedback,
                    "total_time": (datetime.now() - start_time).total_seconds(),
                    "metrics": self.metrics
                }
            )
            
        except Exception as e:
            self.logger.error(f"Pattern application error: {e}")
            self.metrics["failed_applications"] = (
                self.metrics.get("failed_applications", 0) + 1
            )
            
            # Return template result as fallback
            if 'template_result' in locals():
                yield OptimizationStream(
                    interim_result=template_result,
                    confidence_score=0.5,
                    complete=True,
                    metadata={
                        "error": str(e),
                        "fallback": True,
                        "total_time": (datetime.now() - start_time).total_seconds()
                    }
                )
            else:
                yield OptimizationStream(
                    interim_result=prompt,
                    confidence_score=0.0,
                    complete=True,
                    metadata={"error": str(e)}
                )

    def _prepare_requirements(
        self,
        pattern: PatternRegistry,
        context: Optional[StrategyContext]
    ) -> Dict[str, Any]:
        """Prepare requirements for DSPy processing."""
        requirements = {}
        
        # Add pattern-specific requirements
        if pattern.validation_rules:
            requirements.update(pattern.validation_rules)
            
        # Add context-specific requirements
        if context:
            if context.processing_level:
                requirements["processing_level"] = context.processing_level.value
            if context.technical_requirements:
                requirements["technical_requirements"] = context.technical_requirements
                
        return requirements

    async def _update_metrics(
        self,
        pattern_type: PatternCategory,
        confidence: float,
        start_time: datetime
    ):
        """Update pattern metrics."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.metrics["total_applications"] += 1
        self.metrics["successful_applications"] += 1
        
        # Update confidence metrics
        total = self.metrics["total_applications"]
        current_avg = self.metrics["average_confidence"]
        self.metrics["average_confidence"] = (
            (current_avg * (total - 1) + confidence) / total
        )
        
        # Update performance metrics
        self.metrics["performance_metrics"]["avg_application_time"] = (
            (self.metrics["performance_metrics"]["avg_application_time"] * 
             (total - 1) + processing_time) / total
        )
        
        # Update pattern usage
        if pattern_type.value not in self.metrics["pattern_usage"]:
            self.metrics["pattern_usage"][pattern_type.value] = 0
        self.metrics["pattern_usage"][pattern_type.value] += 1
        
        # Update pattern-specific metrics
        pattern = self.pattern_registry[pattern_type]
        pattern.performance_metrics["avg_confidence"] = (
            (pattern.performance_metrics.get("avg_confidence", 0) * 
             (pattern.performance_metrics.get("total_uses", 0)) +
             confidence) / (pattern.performance_metrics.get("total_uses", 0) + 1)
        )
        pattern.performance_metrics["total_uses"] = (
            pattern.performance_metrics.get("total_uses", 0) + 1
        )

    def _initialize_patterns(self):
        """Initialize core optimization patterns."""
        self.pattern_registry[PatternCategory.ANALYSIS] = PatternRegistry(
            metadata=PatternMetadata(
                category=PatternCategory.ANALYSIS,
                complexity_level=2,
                typical_expansion_factor=1.5,
                recommended_processing_level=ProcessingLevel.STANDARD
            ),
            structure=[
                "Key Concepts",
                "Relationships",
                "Implications",
                "Examples"
            ],
            validation_rules={
                "min_concepts": 2,
                "require_examples": True,
                "min_length": 100
            },
            dspy_config=self.dspy_config
        )
        
        self.pattern_registry[PatternCategory.TECHNICAL] = PatternRegistry(
            metadata=PatternMetadata(
                category=PatternCategory.TECHNICAL,
                complexity_level=3,
                typical_expansion_factor=2.0,
                recommended_processing_level=ProcessingLevel.FULL
            ),
            structure=[
                "Technical Overview",
                "Implementation Details",
                "Performance Considerations",
                "Error Handling",
                "Usage Examples"
            ],
            validation_rules={
                "required_sections": [
                    "Implementation Details",
                    "Error Handling",
                    "Usage Examples"
                ],
                "min_length": 200
            },
            dspy_config=self.dspy_config
        )

        self.pattern_registry[PatternCategory.CLARIFICATION] = PatternRegistry(
            metadata=PatternMetadata(
                category=PatternCategory.CLARIFICATION,
                complexity_level=1,
                typical_expansion_factor=1.2,
                recommended_processing_level=ProcessingLevel.STANDARD
            ),
            structure=[
                "Original Question/Statement",
                "Key Points to Clarify",
                "Detailed Explanation",
                "Restated Question/Statement"
            ],
            validation_rules={
                "required_sections": [
                    "Key Points to Clarify",
                    "Detailed Explanation"
                ],
                "min_length": 50
            },
            dspy_config=self.dspy_config
        )

    def _build_context_elements(self, context: Optional[StrategyContext]) -> str:
        """Build context elements string."""
        if not context:
            return ""
            
        elements = []
        if context.domain:
            elements.append(f"Domain: {context.domain}")
            
        if context.technical_requirements:
            elements.append("Technical Requirements:")
            for key, value in context.technical_requirements.items():
                elements.append(f"  - {key}: {value}")
        
        if context.semantic_requirements:
            elements.append("Semantic Requirements:")
            for req in context.semantic_requirements:
                elements.append(f"  - {req}")
                
        return "\n".join(elements)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pattern metrics."""
        return {
            "application_stats": {
                "total_applications": self.metrics["total_applications"],
                "successful_applications": self.metrics["successful_applications"],
                "failed_applications": self.metrics.get("failed_applications", 0),
                "average_confidence": self.metrics["average_confidence"]
            },
            "performance": {
                "avg_application_time": self.metrics["performance_metrics"]["avg_application_time"],
                "avg_validation_time": self.metrics["performance_metrics"]["avg_validation_time"]
            },
            "validation": {
                "total_validations": self.metrics["validation_metrics"]["total_validations"],
                "failed_validations": self.metrics["validation_metrics"]["failed_validations"]
            },
            "pattern_usage": self.metrics["pattern_usage"],
            "pattern_specific": {
                pattern_type: {
                    "avg_confidence": pattern.performance_metrics.get("avg_confidence", 0),
                    "total_uses": pattern.performance_metrics.get("total_uses", 0),
                    "last_validation": pattern.last_validation.isoformat() if pattern.last_validation else None
                }
                for pattern_type, pattern in self.pattern_registry.items()
            }
        }

    async def is_healthy(self) -> bool:
        """Check pattern system health."""
        try:
            if self.component_state != ComponentState.READY:
                return False

            # Check pattern registry
            if not self.pattern_registry:
                return False

            # Verify patterns are properly initialized
            for pattern in self.pattern_registry.values():
                if not pattern.structure or not pattern.validation_rules:
                    return False

            # Check DSPy configuration
            if not self.dspy_config or not self.lm:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def cleanup(self):
        """Cleanup pattern system resources."""
        try:
            self.component_state = ComponentState.SHUTTING_DOWN

            # Close DSPy resources
            if self.lm:
                await self.lm.aclose()

            # Clear registries and metrics
            self.pattern_registry.clear()
            self.metrics.clear()

            self.component_state = ComponentState.UNINITIALIZED
            self.logger.info("Pattern system cleanup completed")

        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            self.component_state = ComponentState.ERROR
            raise