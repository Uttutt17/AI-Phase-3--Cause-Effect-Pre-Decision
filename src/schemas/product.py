"""Product-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class ProductAttributeResponse(BaseModel):
    """Product attribute response schema."""
    attribute_name: str
    attribute_type: str
    attribute_value: Union[str, int, float, bool, List[str]]
    unit: Optional[str] = None
    display_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class VisualAssetResponse(BaseModel):
    """Visual asset response schema."""
    asset_type: str
    asset_url: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="asset_metadata")  # Maps to asset_metadata in model
    
    class Config:
        from_attributes = True
        populate_by_name = True


class ProductResponse(BaseModel):
    """Product response schema."""
    id: int
    product_id: str
    name: str
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductFullResponse(BaseModel):
    """Full product response with attributes and assets."""
    id: int
    product_id: str
    name: str
    category: Optional[str] = None
    attributes: List[ProductAttributeResponse] = []
    visual_assets: List[VisualAssetResponse] = []
    
    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    """Product creation schema."""
    product_id: str
    name: str
    category: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    visual_assets: Dict[str, Union[str, List[str]]] = Field(default_factory=dict)

