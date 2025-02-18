"""
MCP Server Implementation Package
"""

# Version information
__version__ = "2.0.0"  # Updated to match new protocol version
PROTOCOL_VERSION = "2.0.0"
MINIMAL_COMPATIBLE_VERSION = "2.0.0"

# Core types and errors
from .shared_types import (
    ErrorCodes,
    OptimizationErrorType,
    MCPVersion,
    ProtocolError,
    OptimizationError,
    VersionError,
    PatternCategory,
    StrategyPhase,
    MessageType,
    TransportType,
    DSPyConfig,
    OptimizationStream,
    PatternResult,
    StrategyResult,
    TransportMetrics
)

# Protocol and message models
from .models import (
    ProtocolMessage,
    ProtocolResponse,
    ProtocolMethod,
    ProcessingLevel,
    OptimizationType,
    ValidationLevel,
    InitializationRequest,
    InitializationResponse,
    OptimizationGoal,
    OptimizationContext,
    OptimizationStep,
    OptimizationResult
)

from typing import Optional, Dict, Any


__all__ = [
    # Protocol Models
    "ProtocolMessage",
    "ProtocolResponse",
    "ProtocolMethod",
    "InitializationRequest",
    "InitializationResponse",

    # Optimization Models
    "OptimizationGoal",
    "OptimizationContext",
    "OptimizationStep",
    "OptimizationResult",
    "OptimizationStream",
    "PatternResult",
    "StrategyResult",

    # Types and Enums
    "OptimizationType",
    "ProcessingLevel",
    "ValidationLevel",
    "ErrorCodes",
    "OptimizationErrorType",
    "MCPVersion",
    "PatternCategory",
    "StrategyPhase",
    "MessageType",
    "TransportType",
    "TransportMetrics",
    "DSPyConfig",

    # Errors
    "ProtocolError",
    "OptimizationError",
    "VersionError",

    # Version Information
    "__version__",
    "PROTOCOL_VERSION",
    "MINIMAL_COMPATIBLE_VERSION"
]

def create_optimizer(
    config: Optional[Dict[str, Any]] = None,
    dspy_config: Optional[DSPyConfig] = None
) -> 'EnhancedPromptOptimizer':
    """Create an instance of the enhanced prompt optimizer."""
    from .prompt_optimizer import EnhancedPromptOptimizer
    return EnhancedPromptOptimizer(config, dspy_config)

# Version compatibility check
VERSION = MCPVersion.parse(__version__)
if not VERSION.is_compatible(MINIMAL_COMPATIBLE_VERSION):
    raise VersionError(
        "Incompatible version",
        VERSION,
        MINIMAL_COMPATIBLE_VERSION
    )