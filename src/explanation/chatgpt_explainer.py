"""Main ChatGPT explanation generator."""
from typing import Dict, Any, List
from src.api.chatgpt_client import ChatGPTClient
from src.explanation.prompt_templates import generate_explanation_prompt
from src.schemas.explanation import ExplanationRequest, ExplanationResponse


class ChatGPTExplainer:
    """Main explanation generator using ChatGPT."""
    
    def __init__(self):
        self.client = ChatGPTClient()
    
    def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Generate explanation for visualization.
        
        Args:
            request: ExplanationRequest with all necessary data
        
        Returns:
            ExplanationResponse with generated explanation
        """
        # Format selected attributes for prompt
        # Assuming selected_attributes is a dict of {product_id: {attr: value}}
        formatted_attributes = request.selected_attributes
        
        # Generate prompt
        prompt = generate_explanation_prompt(
            selected_attributes=formatted_attributes,
            visual_effects_applied=request.visual_effects_applied,
            user_intent=request.user_intent,
            products=request.products,
            user_query=request.user_query
        )
        
        # Generate explanation
        explanation = self.client.generate_explanation(prompt)
        
        # Validate response
        source_data = {
            "attributes": request.selected_attributes,
            "products": request.products
        }
        verified = self.client.validate_response(explanation, source_data)
        
        return ExplanationResponse(
            explanation=explanation,
            confidence=0.9 if verified else 0.5,
            source_data_verified=verified
        )

