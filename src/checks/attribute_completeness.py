"""Attribute completeness check."""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.data.product_service import ProductService


class AttributeCompletenessCheck:
    """Checks if all required attributes are available for products."""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def check(
        self,
        db: Session,
        product_ids: List[str],
        required_attributes: List[str]
    ) -> Dict[str, Any]:
        """
        Check attribute completeness.
        
        Returns:
            Dict with 'passed' (bool), 'missing_attributes' (List[str]), 'coverage' (float)
        """
        if not product_ids or not required_attributes:
            return {
                "passed": False,
                "missing_attributes": required_attributes,
                "coverage": 0.0,
                "message": "No products or attributes specified"
            }
        
        # Get attributes for all products
        products_attributes = self.product_service.get_products_attributes(db, product_ids)
        
        # Check which attributes are missing
        missing_attributes = []
        available_count = 0
        
        for attr in required_attributes:
            attr_available = False
            for product_id, attrs in products_attributes.items():
                if attr in attrs:
                    attr_available = True
                    break
            
            if attr_available:
                available_count += 1
            else:
                missing_attributes.append(attr)
        
        coverage = available_count / len(required_attributes) if required_attributes else 0.0
        passed = coverage >= 0.8  # 80% coverage threshold
        
        return {
            "passed": passed,
            "missing_attributes": missing_attributes,
            "coverage": coverage,
            "available_count": available_count,
            "total_count": len(required_attributes),
            "message": f"Attribute coverage: {coverage:.1%}" if passed else f"Missing attributes: {', '.join(missing_attributes)}"
        }

