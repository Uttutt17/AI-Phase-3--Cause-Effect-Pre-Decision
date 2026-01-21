"""Visualization engine for rendering visual effects."""
from typing import List, Dict, Any
from src.schemas.visualization import VisualEffect, VisualizationResponse


class VisualizationEngine:
    """Engine for generating visualization data."""
    
    def apply_visual_effects(
        self,
        visualization_response: VisualizationResponse
    ) -> Dict[str, Any]:
        """
        Apply visual effects to visualization data.
        
        Args:
            visualization_response: VisualizationResponse with products and effects
        
        Returns:
            Enhanced visualization data with effect instructions
        """
        visualization_data = visualization_response.visualization_data.copy()
        visualization_data["effects"] = []
        
        for effect in visualization_response.visual_effects:
            effect_data = self._generate_effect_data(
                effect,
                visualization_response.product_ids,
                visualization_response.selected_attributes,
                visualization_data
            )
            visualization_data["effects"].append(effect_data)
        
        return visualization_data
    
    def _generate_effect_data(
        self,
        effect: VisualEffect,
        product_ids: List[str],
        attributes: List[str],
        visualization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate data for a specific visual effect."""
        effect_map = {
            VisualEffect.SPLIT_SCREEN: {
                "type": "split_screen",
                "products": product_ids,
                "layout": "side_by_side"
            },
            VisualEffect.HIGHLIGHT_DIFFERENCES: {
                "type": "highlight",
                "target": "differences",
                "attributes": attributes
            },
            VisualEffect.HIGHLIGHT_MATERIALS: {
                "type": "highlight",
                "target": "materials",
                "attributes": [attr for attr in attributes if "material" in attr.lower()]
            },
            VisualEffect.ZOOM_EARCUP_FRAME: {
                "type": "zoom",
                "target": "earcup_frame",
                "magnification": 1.5
            },
            VisualEffect.SHOW_SPEC_CALLOUTS: {
                "type": "callout",
                "target": "specs",
                "attributes": attributes
            },
            VisualEffect.WEIGHT_LABEL: {
                "type": "label",
                "target": "weight",
                "position": "top_right"
            },
            VisualEffect.COMFORT_INDICATOR: {
                "type": "indicator",
                "target": "comfort",
                "attributes": [attr for attr in attributes if attr in ["weight", "clamp_force", "padding_material"]]
            },
            VisualEffect.COMPARISON_VS_LIGHTER: {
                "type": "comparison",
                "target": "weight_comparison",
                "reference": "lighter_products"
            },
            VisualEffect.HIGHLIGHT_TRAVEL_SPECS: {
                "type": "highlight",
                "target": "travel_specs",
                "attributes": [attr for attr in attributes if attr in ["weight", "foldability", "battery_life", "case_size"]]
            },
            VisualEffect.DIM_IRRELEVANT_SPECS: {
                "type": "dim",
                "target": "irrelevant",
                "keep_highlighted": attributes
            }
        }
        
        return effect_map.get(effect, {"type": "unknown", "effect": str(effect)})

