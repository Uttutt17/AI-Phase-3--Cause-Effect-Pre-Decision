"""Intent to attribute and visual effect mappings."""
from typing import Dict, List
from src.schemas.visualization import VisualEffect


# Intent → Attribute → Visual Effect mappings
INTENT_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    "compare": {
        "attributes": [
            "price", "weight", "battery_life", "noise_cancellation", "usage_context"
        ],
        "visual_effects": [
            VisualEffect.SPLIT_SCREEN,
            VisualEffect.HIGHLIGHT_DIFFERENCES
        ]
    },
    "explain_price": {
        "attributes": [
            "material", "build_quality", "driver_type", "noise_cancellation_level"
        ],
        "visual_effects": [
            VisualEffect.HIGHLIGHT_MATERIALS,
            VisualEffect.ZOOM_EARCUP_FRAME,
            VisualEffect.SHOW_SPEC_CALLOUTS
        ]
    },
    "explain": {
        "attributes": [
            "material", "build_quality", "driver_type", "noise_cancellation_level"
        ],
        "visual_effects": [
            VisualEffect.HIGHLIGHT_MATERIALS,
            VisualEffect.SHOW_SPEC_CALLOUTS
        ]
    },
    "clarify_comfort": {
        "attributes": [
            "weight", "clamp_force", "padding_material"
        ],
        "visual_effects": [
            VisualEffect.WEIGHT_LABEL,
            VisualEffect.COMFORT_INDICATOR,
            VisualEffect.COMPARISON_VS_LIGHTER
        ]
    },
    "clarify": {
        "attributes": [
            "weight", "clamp_force", "padding_material", "fit", "size"
        ],
        "visual_effects": [
            VisualEffect.WEIGHT_LABEL,
            VisualEffect.COMFORT_INDICATOR
        ]
    },
    "usage_context": {
        "attributes": [
            "weight", "foldability", "battery_life", "case_size"
        ],
        "visual_effects": [
            VisualEffect.HIGHLIGHT_TRAVEL_SPECS,
            VisualEffect.DIM_IRRELEVANT_SPECS
        ]
    },
    "choose": {
        "attributes": [
            "price", "weight", "battery_life", "noise_cancellation",
            "usage_context", "foldability", "case_size"
        ],
        "visual_effects": [
            VisualEffect.SPLIT_SCREEN,
            VisualEffect.HIGHLIGHT_DIFFERENCES,
            VisualEffect.HIGHLIGHT_TRAVEL_SPECS
        ]
    }
}


def get_attributes_for_intent(intent_type: str, context: Dict = None) -> List[str]:
    """Get attributes for a given intent type."""
    context = context or {}
    
    # Check for specific intent subtypes
    if intent_type == "explain" and "price" in str(context.get("mentioned_attributes", [])).lower():
        intent_key = "explain_price"
    elif intent_type == "clarify" and any(kw in str(context).lower() for kw in ["comfort", "fit", "weight"]):
        intent_key = "clarify_comfort"
    elif "usage_context" in context or "travel" in str(context).lower():
        intent_key = "usage_context"
    else:
        intent_key = intent_type
    
    mapping = INTENT_MAPPINGS.get(intent_key, INTENT_MAPPINGS.get(intent_type, {}))
    return mapping.get("attributes", [])


def get_visual_effects_for_intent(intent_type: str, context: Dict = None) -> List[VisualEffect]:
    """Get visual effects for a given intent type."""
    context = context or {}
    
    # Check for specific intent subtypes
    if intent_type == "explain" and "price" in str(context.get("mentioned_attributes", [])).lower():
        intent_key = "explain_price"
    elif intent_type == "clarify" and any(kw in str(context).lower() for kw in ["comfort", "fit", "weight"]):
        intent_key = "clarify_comfort"
    elif "usage_context" in context or "travel" in str(context).lower():
        intent_key = "usage_context"
    else:
        intent_key = intent_type
    
    mapping = INTENT_MAPPINGS.get(intent_key, INTENT_MAPPINGS.get(intent_type, {}))
    return mapping.get("visual_effects", [])

