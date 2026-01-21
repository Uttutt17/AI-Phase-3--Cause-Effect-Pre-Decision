"""Prompt templates for ChatGPT explanations."""
from typing import Dict, Any, List


def generate_explanation_prompt(
    selected_attributes: Dict[str, Any],
    visual_effects_applied: List[str],
    user_intent: str,
    products: List[str],
    user_query: str = None
) -> str:
    """
    Generate explanation prompt for ChatGPT.
    
    Args:
        selected_attributes: Dictionary of selected attributes and values
        visual_effects_applied: List of visual effects applied
        user_intent: Detected user intent
        products: List of product names/IDs
        user_query: Original user query
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are explaining product attributes to a user. Your role is to provide clear, helpful explanations based ONLY on the data provided below.

CRITICAL RULES - YOU MUST FOLLOW THESE:
DO NOT:
- Invent or guess product data
- Make purchase recommendations
- Create new attributes
- Access product database
- Provide information not in the data below

DO:
- Explain why these specific attributes were selected
- Describe what the visual effects show
- Use ONLY the exact attribute values provided below
- Provide context about what the attributes mean
- Be helpful and clear

User Intent: {user_intent}
Products: {', '.join(products)}
User Query: {user_query or 'Not provided'}

Selected Attributes and Values:
"""
    
    # Add attribute data
    for product, attrs in selected_attributes.items():
        prompt += f"\n{product}:\n"
        for attr_name, attr_value in attrs.items():
            prompt += f"  - {attr_name}: {attr_value}\n"
    
    prompt += f"\nVisual Effects Applied: {', '.join(visual_effects_applied)}\n"
    prompt += "\nProvide a clear, helpful explanation of why these attributes were shown and what they mean for the user's decision."
    
    return prompt


def generate_attribute_explanation_prompt(
    attribute_name: str,
    attribute_value: Any,
    product_name: str,
    user_query: str = None
) -> str:
    """Generate prompt for explaining a specific attribute."""
    prompt = f"""Explain what the attribute '{attribute_name}' means for the product '{product_name}' with the value '{attribute_value}'.

User's question: {user_query or 'General inquiry'}

Provide a clear, helpful explanation. Do NOT invent additional information about the product."""
    return prompt


def generate_comparison_prompt(
    products: List[str],
    comparison_data: Dict[str, Dict[str, Any]],
    user_query: str = None
) -> str:
    """Generate prompt for comparison explanation."""
    prompt = f"""You are comparing products for a user. Explain the differences between the products based ONLY on the data provided.

User Query: {user_query or 'Compare products'}

Comparison Data:
"""
    
    for attr_name, attr_values in comparison_data.items():
        prompt += f"\n{attr_name}:\n"
        for product, value in attr_values.items():
            prompt += f"  - {product}: {value}\n"
    
    prompt += "\nProvide a clear comparison explanation. Highlight key differences. Do NOT invent data or make recommendations."
    return prompt

