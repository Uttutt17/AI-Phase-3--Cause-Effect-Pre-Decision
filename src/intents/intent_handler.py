"""Intent handler that processes intents and returns visualization data."""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.intents.intent_detector import IntentDetector
from src.intents.intent_mappings import get_attributes_for_intent, get_visual_effects_for_intent
from src.data.product_service import ProductService
from src.schemas.intent import IntentResponse
from src.schemas.visualization import VisualizationResponse, VisualEffect


class IntentHandler:
    """Handles intent processing and attribute selection."""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.product_service = ProductService()
    
    def process_intent(
        self,
        db: Session,
        user_query: str,
        product_ids: List[str] = None
    ) -> tuple[IntentResponse, VisualizationResponse]:
        """
        Process user query: detect intent and generate visualization response.
        
        Returns:
            Tuple of (IntentResponse, VisualizationResponse)
        """
        # Detect intent
        intent_response = self.intent_detector.detect_intent(user_query, product_ids)
        
        # Get product IDs from intent if not provided
        if not product_ids:
            product_ids = intent_response.detected_products
        
        if not product_ids:
            # No products detected, return empty visualization
            return intent_response, VisualizationResponse(
                product_ids=[],
                selected_attributes=[],
                visual_effects=[],
                message="No products detected in query. Please specify product names or IDs."
            )
        
        # Get attributes for intent
        context = intent_response.extracted_context or {}
        selected_attributes = get_attributes_for_intent(
            intent_response.intent_type.value,
            context
        )
        
        # Filter attributes that exist in products
        products_attributes = self.product_service.get_products_attributes(db, product_ids)
        available_attributes = self._filter_available_attributes(
            selected_attributes,
            products_attributes
        )
        
        # Get visual effects
        visual_effects = get_visual_effects_for_intent(
            intent_response.intent_type.value,
            context
        )
        
        # Build visualization data
        visualization_data = self._build_visualization_data(
            product_ids,
            available_attributes,
            products_attributes
        )
        
        visualization_response = VisualizationResponse(
            product_ids=product_ids,
            selected_attributes=available_attributes,
            visual_effects=visual_effects,
            visualization_data=visualization_data
        )
        
        return intent_response, visualization_response
    
    def _filter_available_attributes(
        self,
        requested_attributes: List[str],
        products_attributes: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Filter attributes to only include those available in products."""
        if not products_attributes:
            return []
        
        # Get intersection of all product attributes
        all_product_attrs = set()
        for product_attrs in products_attributes.values():
            all_product_attrs.update(product_attrs.keys())
        
        # Return requested attributes that exist in at least one product
        available = [attr for attr in requested_attributes if attr in all_product_attrs]
        return available
    
    def _build_visualization_data(
        self,
        product_ids: List[str],
        attributes: List[str],
        products_attributes: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build visualization data structure."""
        data = {
            "products": {},
            "comparison": {}
        }
        
        for product_id in product_ids:
            product_attrs = products_attributes.get(product_id, {})
            data["products"][product_id] = {
                attr: product_attrs.get(attr) for attr in attributes if attr in product_attrs
            }
        
        # Build comparison data if multiple products
        if len(product_ids) > 1:
            for attr in attributes:
                values = {}
                for product_id in product_ids:
                    product_attrs = products_attributes.get(product_id, {})
                    if attr in product_attrs:
                        values[product_id] = product_attrs[attr]
                if values:
                    data["comparison"][attr] = values
        
        return data

