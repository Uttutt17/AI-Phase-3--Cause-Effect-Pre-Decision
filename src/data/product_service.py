"""Product data service for managing product information."""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from src.models.product import Product, ProductAttribute, VisualAsset
from src.schemas.product import ProductCreate, ProductFullResponse
import json


class ProductService:
    """Service for managing product data."""
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        """Get product by product_id."""
        return db.query(Product).filter(Product.product_id == product_id).first()
    
    @staticmethod
    def get_all_products(db: Session) -> List[Product]:
        """Get all products."""
        return db.query(Product).all()
    
    @staticmethod
    def get_product_attributes(db: Session, product_id: str) -> Dict[str, Any]:
        """Get all attributes for a product as a dictionary."""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return {}
        
        attributes = {}
        for attr in product.attributes:
            # Parse attribute value based on type
            if attr.attribute_type == "number":
                try:
                    attributes[attr.attribute_name] = float(attr.attribute_value)
                except ValueError:
                    attributes[attr.attribute_name] = attr.attribute_value
            elif attr.attribute_type == "boolean":
                attributes[attr.attribute_name] = attr.attribute_value.lower() == "true"
            elif attr.attribute_type == "array":
                try:
                    attributes[attr.attribute_name] = json.loads(attr.attribute_value)
                except json.JSONDecodeError:
                    attributes[attr.attribute_name] = [attr.attribute_value]
            else:
                attributes[attr.attribute_name] = attr.attribute_value
        
        return attributes
    
    @staticmethod
    def get_products_attributes(db: Session, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get attributes for multiple products."""
        result = {}
        for product_id in product_ids:
            result[product_id] = ProductService.get_product_attributes(db, product_id)
        return result
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product with attributes and visual assets."""
        # Create product
        product = Product(
            product_id=product_data.product_id,
            name=product_data.name,
            category=product_data.category
        )
        db.add(product)
        db.flush()
        
        # Create attributes
        for attr_name, attr_value in product_data.attributes.items():
            attr_type = ProductService._infer_attribute_type(attr_value)
            attr_value_str = json.dumps(attr_value) if isinstance(attr_value, (list, dict)) else str(attr_value)
            
            attribute = ProductAttribute(
                product_id=product.id,
                attribute_name=attr_name,
                attribute_type=attr_type,
                attribute_value=attr_value_str
            )
            db.add(attribute)
        
        # Create visual assets
        for asset_type, asset_data in product_data.visual_assets.items():
            if isinstance(asset_data, list):
                for url in asset_data:
                    asset = VisualAsset(
                        product_id=product.id,
                        asset_type=asset_type,
                        asset_url=url
                    )
                    db.add(asset)
            else:
                asset = VisualAsset(
                    product_id=product.id,
                    asset_type=asset_type,
                    asset_url=asset_data
                )
                db.add(asset)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def _infer_attribute_type(value: Any) -> str:
        """Infer attribute type from value."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, list):
            return "array"
        else:
            return "string"
    
    @staticmethod
    def attribute_exists(db: Session, product_id: str, attribute_name: str) -> bool:
        """Check if an attribute exists for a product."""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return False
        return any(attr.attribute_name == attribute_name for attr in product.attributes)
    
    @staticmethod
    def get_visual_assets(db: Session, product_id: str) -> List[VisualAsset]:
        """Get visual assets for a product."""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return []
        return product.visual_assets

