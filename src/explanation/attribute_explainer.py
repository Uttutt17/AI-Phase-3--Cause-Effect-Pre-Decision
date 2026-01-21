"""Attribute-specific explanation generator."""
from typing import Any
from src.api.chatgpt_client import ChatGPTClient
from src.explanation.prompt_templates import generate_attribute_explanation_prompt


class AttributeExplainer:
    """Explains specific product attributes."""
    
    def __init__(self):
        self.client = ChatGPTClient()
    
    def explain_attribute(
        self,
        attribute_name: str,
        attribute_value: Any,
        product_name: str,
        user_query: str = None
    ) -> str:
        """
        Explain a specific attribute.
        
        Args:
            attribute_name: Name of the attribute
            attribute_value: Value of the attribute
            product_name: Name of the product
            user_query: Optional user query for context
        
        Returns:
            Explanation text
        """
        prompt = generate_attribute_explanation_prompt(
            attribute_name=attribute_name,
            attribute_value=attribute_value,
            product_name=product_name,
            user_query=user_query
        )
        
        return self.client.generate_explanation(prompt)

