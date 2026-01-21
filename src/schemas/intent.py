"""Intent-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class IntentType(str, Enum):
    """Intent type enumeration."""
    COMPARE = "compare"
    EXPLAIN = "explain"
    CLARIFY = "clarify"
    CHOOSE = "choose"
    UNKNOWN = "unknown"


class IntentRequest(BaseModel):
    """Intent detection request schema."""
    user_query: str = Field(..., description="User's natural language query")
    product_ids: Optional[List[str]] = Field(None, description="Optional product IDs mentioned in query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class IntentResponse(BaseModel):
    """Intent detection response schema."""
    intent_type: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    detected_products: List[str] = Field(default_factory=list)
    extracted_context: Optional[Dict[str, Any]] = None

