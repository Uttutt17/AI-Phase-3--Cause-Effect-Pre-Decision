"""Visualization-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class VisualEffect(str, Enum):
    """Visual effect types."""
    SPLIT_SCREEN = "split_screen"
    HIGHLIGHT_DIFFERENCES = "highlight_differences"
    HIGHLIGHT_MATERIALS = "highlight_materials"
    ZOOM_EARCUP_FRAME = "zoom_earcup_frame"
    SHOW_SPEC_CALLOUTS = "show_spec_callouts"
    WEIGHT_LABEL = "weight_label"
    COMFORT_INDICATOR = "comfort_indicator"
    COMPARISON_VS_LIGHTER = "comparison_vs_lighter"
    HIGHLIGHT_TRAVEL_SPECS = "highlight_travel_specs"
    DIM_IRRELEVANT_SPECS = "dim_irrelevant_specs"


class VisualizationRequest(BaseModel):
    """Visualization request schema."""
    intent_type: str
    product_ids: List[str]
    selected_attributes: List[str]
    user_query: Optional[str] = None


class VisualizationResponse(BaseModel):
    """Visualization response schema."""
    product_ids: List[str]
    selected_attributes: List[str]
    visual_effects: List[VisualEffect]
    visualization_data: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None

