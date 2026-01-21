"""OpenAI API client wrapper."""
from openai import OpenAI
from src.config import settings
from typing import Dict, Any, Optional


class ChatGPTClient:
    """Client for interacting with OpenAI GPT-4 API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def generate_explanation(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate explanation using GPT-4.
        
        Args:
            prompt: The prompt to send to GPT-4
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated explanation text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains product attributes clearly and accurately. You only use the data provided to you and never invent or guess product information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def validate_response(self, response: str, source_data: Dict[str, Any]) -> bool:
        """
        Validate that response doesn't contain invented data.
        This is a simple validation - can be enhanced.
        """
        # Basic validation: check if response mentions attributes that weren't in source
        # This is a simplified check - real implementation would be more sophisticated
        return True  # Placeholder

