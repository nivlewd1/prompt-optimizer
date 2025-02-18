"""
Enhanced Model Context Protocol Models Implementation

This module defines the data models and validation for the MCP protocol,
with improved version handling and validation.
"""

from typing import Dict, List, Optional, Any, Set, Union, Literal, Tuple, AsyncGenerator
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from dataclasses import dataclass, field
import json
from uuid import uuid4

from .shared_types import (
    OptimizationType,
    ProcessingLevel,
    ValidationLevel,
    StrategyContext,
    PatternCategory,
    MessageType,
    MCPVersion,
    VersionError,
    TransportConfig,
    TransportType,
    ProtocolError,
    DSPyConfig,
    OptimizationStream,
    SecurityContext,
    RateLimitConfig,
    StreamState,
    StreamingConfig,
    MetricsData
)

# --- Protocol Models ---

class ProtocolMethod(str, Enum):
    """Defines the supported protocol methods."""
    INITIALIZE = "initialize"
    OPTIMIZE_PROMPT = "optimize_prompt"
    SHUTDOWN = "shutdown"
    STATUS = "status"
    # Added conversation methods
    CONVERSATION_START = "conversation.start"
    CONVERSATION_MESSAGE = "conversation.message"
    CONVERSATION_END = "conversation.end"

class ProtocolMessage(BaseModel):
    """Base model for protocol messages."""
    method: ProtocolMethod
    msg_type: MessageType  # New field for message type
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    jsonrpc: Literal["2.0"] = "2.0"
    version: Optional[str] = Field(default="2.0.0")  # Added version field
    security_context: Optional[SecurityContext] = None  # Add security context

    @model_validator(mode='after')
    def validate_method(cls, values):
        """Ensure method is supported and verify version compatibility."""
        method = values.method
        if not method:
            raise ValueError("Method name cannot be empty")
        if method not in ProtocolMethod:
            raise ValueError(f"Unsupported method: {method}")

        # Version compatibility check
        if values.version:
            try:
                version = MCPVersion.parse(values.version)
                if not version.is_compatible("2.0.0"):  # Base compatibility version
                    raise VersionError(
                        f"Incompatible protocol version: {values.version}",
                        version,
                        values.version
                    )
            except ValueError as e:
                raise ValueError(f"Invalid version format: {str(e)}")

        return values

    @model_validator(mode='after')
    def validate_message_type(cls, values):
        """Validate message type against method."""
        method = values.method
        msg_type = values.msg_type
        
        method_type_mapping = {
            ProtocolMethod.INITIALIZE: MessageType.REQUEST,
            ProtocolMethod.OPTIMIZE_PROMPT: MessageType.REQUEST,
            ProtocolMethod.SHUTDOWN: MessageType.CONTROL,
            ProtocolMethod.STATUS: MessageType.REQUEST,
            ProtocolMethod.CONVERSATION_START: MessageType.NOTIFICATION,
            ProtocolMethod.CONVERSATION_MESSAGE: MessageType.NOTIFICATION,
            ProtocolMethod.CONVERSATION_END: MessageType.NOTIFICATION
        }
        
        if method not in method_type_mapping:
            raise ValueError(f"No message type mapping for method: {method}")
            
        if msg_type != method_type_mapping[method]:
            raise ValueError(
                f"Message type {msg_type} is invalid for method {method}. "
                f"Expected {method_type_mapping[method]}"
            )
            
        return values

class ProtocolResponse(BaseModel):
    """Base model for protocol responses."""
    msg_type: MessageType = MessageType.RESPONSE  # New field with default value
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    jsonrpc: Literal["2.0"] = "2.0"
    version: Optional[str] = Field(default="2.0.0")  # Added version field

    @model_validator(mode='after')
    def validate_response(cls, values):
        """Ensure response has either result or error and verify version compatibility."""
        if values.result is not None and values.error is not None:
            raise ValueError("Response cannot have both result and error")
        if values.error is not None:
            if not isinstance(values.error, dict):
                raise ValueError("Error must be a dictionary")
            required_fields = {'code', 'message'}
            if not required_fields.issubset(values.error):
                raise ValueError("Error must contain 'code' and 'message'")

        # Version compatibility check
        if values.version:
            try:
                version = MCPVersion.parse(values.version)
                if not version.is_compatible("2.0.0"):  # Base compatibility version
                    raise VersionError(
                        f"Incompatible protocol version: {values.version}",
                        version,
                        values.version
                    )
            except ValueError as e:
                raise ValueError(f"Invalid version format: {str(e)}")

        return values

    @model_validator(mode='after')
    def validate_response_type(cls, values):
        """Validate response type consistency."""
        if values.result and values.msg_type != MessageType.RESPONSE:
            raise ValueError("Result requires RESPONSE message type")
            
        if values.error and values.msg_type != MessageType.ERROR:
            raise ValueError("Error requires ERROR message type")
            
        return values

# --- Optimization Models ---

class StyleGuide(BaseModel):
    """Style guide for optimization."""
    tone: Optional[str] = None
    format: Optional[str] = None
    audience: Optional[str] = None
    technical_level: Optional[str] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_style_guide(cls, values):
        """Validate style guide parameters."""
        if values.technical_level:
            valid_levels = {'basic', 'intermediate', 'advanced'}
            if values.technical_level not in valid_levels:
                raise ValueError(
                    f"Invalid technical level. Must be one of: {valid_levels}"
                )
        return values

class OptimizationGoal(BaseModel):
    """Defines an optimization goal with parameters."""
    type: OptimizationType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_goal(cls, values):
        """Validate optimization goal parameters."""
        if values.weight is not None:
            if not 0.0 <= values.weight <= 1.0:
                raise ValueError("Weight must be between 0.0 and 1.0")
        return values

class OptimizationStreamConfig(BaseModel):
    """Configuration for optimization streaming."""
    chunk_size: int = Field(default=1000, gt=0)
    max_buffer_size: int = Field(default=5000, gt=0)
    backpressure_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    timeout_seconds: float = Field(default=30.0, gt=0)

class OptimizationContext(BaseModel):
    """Context for optimization."""
    domain: Optional[str] = None
    prerequisite_knowledge: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    technical_requirements: Dict[str, Any] = Field(default_factory=dict)
    dspy_parameters: Optional[Dict[str, Any]] = None  # Added DSPyConfig support
    stream_config: Optional[StreamingConfig] = None
    security_context: Optional[SecurityContext] = None

    @model_validator(mode='after')
    def validate_dspy_parameters(cls, values):
        """Validate DSPy parameters in the optimization context."""
        if values.dspy_parameters:
            # Validate DSPy specific parameters
            required_fields = {'model_name', 'temperature'}
            if not required_fields.issubset(values.dspy_parameters):
                missing = required_fields - set(values.dspy_parameters.keys())
                raise ValueError(f"Missing required DSPy parameters: {missing}")
        return values

    @model_validator(mode='after')
    def validate_stream_config(cls, values):
        """Validate stream config in the optimization context."""
        if values.stream_config:
            if values.stream_config.chunk_size <= 0:
                raise ValueError("Chunk size must be positive")
        return values

class PromptOptimizationRequest(BaseModel):
    """Request model for prompt optimization."""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    base_prompt: str = Field(..., min_length=1)
    optimization_goals: List[OptimizationGoal] = Field(..., min_items=1)
    processing_level: ProcessingLevel = Field(default=ProcessingLevel.STANDARD)
    style_guide: Optional[StyleGuide] = None
    context: Optional[OptimizationContext] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    dspy_config: Optional[DSPyConfig] = None
    stream: bool = Field(default=True)                # Added streaming support
    stream_chunk_size: Optional[int] = Field(default=1000, gt=0)  # Added streaming chunk size

    @model_validator(mode='after')
    def validate_request(cls, values):
        """Validate complete request."""
        if not values.base_prompt.strip():
            raise ValueError("Base prompt cannot be empty")
        if not values.optimization_goals:
            raise ValueError("At least one optimization goal is required")
        return values

class OptimizationMetrics(BaseModel):
    """Enhanced metrics for optimization results."""
    accuracy: float = Field(default=1.0, ge=0.0, le=1.0)
    efficiency: float = Field(default=1.0, ge=0.0, le=1.0)
    resource_usage: Dict[str, Any] = Field(default_factory=dict)

class OptimizationStep(BaseModel):
    """Represents a single optimization step."""
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    optimization_type: OptimizationType
    description: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    optimized_prompt: Optional[str] = None
    pattern_category: Optional[PatternCategory] = None
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)  # Added confidence scoring
    dspy_metadata: Optional[Dict[str, Any]] = None              # Added DSPy metadata

@dataclass
class OptimizationResult:
    """Complete result model for optimized prompts."""
    prompt: str
    optimized_prompt: str
    confidence_score: float
    semantic_preservation_score: float = 1.0
    processing_time: float = 0.0
    optimization_steps: List[str] = field(default_factory=list)
    pattern_matches: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    security_context: Optional[SecurityContext] = None
    metrics: Optional[MetricsData] = None

    def validate(self) -> bool:
        """Validate optimization result."""
        return (
            0.0 <= self.confidence_score <= 1.0 and
            0.0 <= self.semantic_preservation_score <= 1.0 and
            len(self.prompt) > 0 and
            len(self.optimized_prompt) > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return self.__dict__

class ResourceAllocationModel(BaseModel):
    """Model for resource allocation requests."""
    resource_type: str
    quantity: int = Field(gt=0)
    priority: int = Field(ge=0, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Session and Status Models ---

class SessionStatus(BaseModel):
    """Status information for a server session."""
    session_id: str = Field(..., description="Unique session identifier")
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    request_count: int = Field(default=0)
    optimization_count: int = Field(default=0)
    active: bool = Field(default=True)

class ServerStatus(BaseModel):
    """Overall server status information."""
    version: str
    uptime: float
    active_sessions: int
    total_optimizations: int
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    initialization_time: datetime = Field(default_factory=datetime.now)

# --- Initialization Models ---

class ClientCapabilities(BaseModel):
    """Enhanced client capability information."""
    version: str
    supported_methods: List[str] = Field(default_factory=list)
    supported_features: Set[str] = Field(default_factory=set)
    max_message_size: Optional[int] = None
    protocol_version: str = Field(default="2.0")
    extensions: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_capabilities(cls, values):
        """Validate client capabilities."""
        # Verify version compatibility
        try:
            version = MCPVersion.parse(values.version)
            if not version.is_compatible("2.0.0"):
                raise VersionError(
                    f"Incompatible client version: {values.version}",
                    version,
                    values.version
                )
        except ValueError as e:
            raise ValueError(f"Invalid version format: {str(e)}")

        # Validate supported methods
        valid_methods = {method.value for method in ProtocolMethod}
        invalid_methods = set(values.supported_methods) - valid_methods
        if invalid_methods:
            raise ValueError(f"Unsupported methods: {invalid_methods}")

        return values

class InitializationRequest(BaseModel):
    """Enhanced initialization request model."""
    capabilities: ClientCapabilities
    client_info: Optional[Dict[str, Any]] = None
    extensions: Dict[str, Any] = Field(default_factory=dict)
    protocol_version: str = Field(default="2.0")

class InitializationResponse(BaseModel):
    """Enhanced initialization response model."""
    capabilities: Dict[str, Any]
    server_info: Dict[str, Any]
    session: Dict[str, Any]
    protocol_version: str = Field(default="2.0")
    extensions: Dict[str, Any] = Field(default_factory=dict)

# --- Conversation Models ---

class ConversationMessage(BaseModel):
    """Single message in a conversation."""
    content: str
    role: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class ConversationState(BaseModel):
    """Tracks the state of an ongoing conversation."""
    conversation_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0)
    optimization_count: int = Field(default=0)
    domain: Optional[str] = None
    technical_level: Optional[str] = None
    active: bool = True

class ConversationOptimizationContext(BaseModel):
    """
    Enhanced context for real-time conversation optimization.
    (Renamed to avoid overshadowing the existing `OptimizationContext`.)
    """
    conversation_history: List[ConversationMessage] = Field(default_factory=list)
    recent_optimizations: List[Dict[str, Any]] = Field(default_factory=list)
    detected_patterns: Dict[str, Any] = Field(default_factory=dict)
    interaction_metrics: Dict[str, float] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

class StreamingOptimizationResponse(BaseModel):
    """Real-time optimization response."""
    message_id: str
    conversation_id: str
    original_content: str
    enhanced_content: str
    confidence_score: float
    is_final: bool = False
    enhancement_type: str
    metadata: Optional[Dict[str, Any]] = None
    metrics: Optional[MetricsData] = None  # Add metrics field
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True

# --- Export Classes ---

__all__ = [
    "ProtocolMethod",
    "ProtocolMessage",
    "ProtocolResponse",
    "StyleGuide",
    "OptimizationGoal",
    "OptimizationContext",           # Original optimization context
    "PromptOptimizationRequest",
    "OptimizationStep",
    "OptimizationResult",
    "OptimizationMetrics",
    "OptimizationStreamConfig",
    "SessionStatus",
    "ServerStatus",
    "ClientCapabilities",
    "InitializationRequest",
    "InitializationResponse",
    "ConversationMessage",
    "ConversationState",
    "ConversationOptimizationContext",
    "StreamingOptimizationResponse",
    "ResourceAllocationModel",
]