"""User context validation check."""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.data.product_service import ProductService


class UserContextCheck:
    """Validates user's stated use case matches available product attributes."""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def check(
        self,
        db: Session,
        product_ids: List[str],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate user context against product attributes.
        
        Returns:
            Dict with 'passed' (bool), 'matched_attributes' (List[str]), 'message' (str)
        """
        if not product_ids:
            return {
                "passed": False,
                "matched_attributes": [],
                "message": "No products specified"
            }
        
        # Get usage context from user context
        usage_context = user_context.get("usage_context")
        mentioned_attributes = user_context.get("mentioned_attributes", [])
        
        if not usage_context and not mentioned_attributes:
            return {
                "passed": True,
                "matched_attributes": [],
                "message": "No specific context to validate"
            }
        
        # Get product attributes
        products_attributes = self.product_service.get_products_attributes(db, product_ids)
        
        matched_attributes = []
        
        # Check if usage_context attribute exists
        if usage_context:
            for product_id, attrs in products_attributes.items():
                if "usage_context" in attrs:
                    usage_contexts = attrs.get("usage_context", [])
                    if isinstance(usage_contexts, list) and usage_context in usage_contexts:
                        matched_attributes.append("usage_context")
                        break
        
        # Check if mentioned attributes exist
        for attr in mentioned_attributes:
            for product_id, attrs in products_attributes.items():
                if attr in attrs:
                    matched_attributes.append(attr)
                    break
        
        passed = len(matched_attributes) > 0 or (not usage_context and not mentioned_attributes)
        
        return {
            "passed": passed,
            "matched_attributes": list(set(matched_attributes)),
            "message": f"Matched attributes: {', '.join(set(matched_attributes))}" if matched_attributes else "No matching attributes found"
        }

