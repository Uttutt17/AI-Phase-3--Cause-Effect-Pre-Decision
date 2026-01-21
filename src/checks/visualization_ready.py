"""Visualization readiness check."""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.data.product_service import ProductService


class VisualizationReadyCheck:
    """Ensures all required visual assets exist."""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def check(
        self,
        db: Session,
        product_ids: List[str],
        required_asset_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Check if products have required visual assets.
        
        Args:
            db: Database session
            product_ids: List of product IDs to check
            required_asset_types: List of required asset types (e.g., ['main_image'])
        
        Returns:
            Dict with 'passed' (bool), 'missing_assets' (Dict), 'message' (str)
        """
        if not product_ids:
            return {
                "passed": False,
                "missing_assets": {},
                "message": "No products specified"
            }
        
        required_asset_types = required_asset_types or ["main_image"]
        missing_assets = {}
        all_ready = True
        
        for product_id in product_ids:
            assets = self.product_service.get_visual_assets(db, product_id)
            asset_types = {asset.asset_type for asset in assets}
            
            missing = [asset_type for asset_type in required_asset_types if asset_type not in asset_types]
            if missing:
                missing_assets[product_id] = missing
                all_ready = False
        
        message = "All products have required visual assets" if all_ready else f"Missing assets: {missing_assets}"
        
        return {
            "passed": all_ready,
            "missing_assets": missing_assets,
            "message": message
        }

