"""
Central Type Definitions for MCP Optimization System

Includes all protocol types, error classes, and data structures
used across the optimization pipeline.
"""

import sys
import os
import platform
import re
from enum import Enum, IntEnum
from typing import (
    Dict, Any, Optional, DefaultDict, Literal, Union,
    List, Set, Tuple, AsyncGenerator
)
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, model_validator
from collections import defaultdict

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
    windows_multiplier: float = Field(default=1.5, ge=1.0, le=5.0)
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
    
    # Constants
    "SIZE_CATEGORIES"
]