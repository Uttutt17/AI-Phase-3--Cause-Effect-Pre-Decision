"""Product data models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database import Base


class Product(Base):
    """Product model with basic information."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    
    # Relationships
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    visual_assets = relationship("VisualAsset", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class ProductAttribute(Base):
    """Product attribute model."""
    __tablename__ = "product_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    attribute_name = Column(String, nullable=False)
    attribute_type = Column(String, nullable=False)  # 'number', 'string', 'boolean', 'array'
    attribute_value = Column(Text, nullable=False)  # JSON string for complex types
    unit = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="attributes")
    
    def __repr__(self):
        return f"<ProductAttribute(name='{self.attribute_name}', value='{self.attribute_value}')>"


class VisualAsset(Base):
    """Visual asset model for product images and callouts."""
    __tablename__ = "visual_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    asset_type = Column(String, nullable=False)  # 'main_image', 'detail_image', 'spec_callout'
    asset_url = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Relationships
    product = relationship("Product", back_populates="visual_assets")
    
    def __repr__(self):
        return f"<VisualAsset(type='{self.asset_type}', url='{self.asset_url}')>"

