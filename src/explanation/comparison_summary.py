"""Comparison summary generator."""
from typing import Dict, Any, List
from src.api.chatgpt_client import ChatGPTClient
from src.explanation.prompt_templates import generate_comparison_prompt


class ComparisonSummary:
    """Generates comparison summaries."""
    
    def __init__(self):
        self.client = ChatGPTClient()
    
    def generate_summary(
        self,
        products: List[str],
        comparison_data: Dict[str, Dict[str, Any]],
        user_query: str = None
    ) -> str:
        """
        Generate comparison summary.
        
        Args:
            products: List of product names
            comparison_data: Dictionary of {attribute: {product: value}}
            user_query: Optional user query
        
        Returns:
            Comparison summary text
        """
        prompt = generate_comparison_prompt(
            products=products,
            comparison_data=comparison_data,
            user_query=user_query
        )
        
        return self.client.generate_explanation(prompt, max_tokens=800)

