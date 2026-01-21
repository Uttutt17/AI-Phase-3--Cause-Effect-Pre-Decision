"""Explanation-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ExplanationRequest(BaseModel):
    """Explanation request schema."""
    user_intent: str
    selected_attributes: Dict[str, Any]
    visual_effects_applied: List[str]
    products: List[str]
    user_query: Optional[str] = None


class ExplanationResponse(BaseModel):
    """Explanation response schema."""
    explanation: str
    confidence: Optional[float] = None
    source_data_verified: bool = True

