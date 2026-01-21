"""Script to seed sample product data."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, engine, Base
from src.models.product import Product, ProductAttribute, VisualAsset
from src.schemas.product import ProductCreate
from src.data.product_service import ProductService

# Create tables
Base.metadata.create_all(bind=engine)

# Sample products data
SAMPLE_PRODUCTS = [
    {
        "product_id": "airpods-max",
        "name": "AirPods Max",
        "category": "Headphones",
        "attributes": {
            "price": 549,
            "weight": 384,
            "battery_life": 20,
            "noise_cancellation": 95,
            "material": "Aluminum",
            "build_quality": "Premium",
            "driver_type": "40mm dynamic",
            "noise_cancellation_level": "Active",
            "clamp_force": 4.2,
            "padding_material": "Memory foam",
            "foldability": False,
            "case_size": "Large",
            "usage_context": ["home", "office", "travel"]
        },
        "visual_assets": {
            "main_image": "https://example.com/airpods-max-main.jpg",
            "detail_images": [
                "https://example.com/airpods-max-detail1.jpg",
                "https://example.com/airpods-max-detail2.jpg"
            ],
            "spec_callouts": [
                "https://example.com/airpods-max-spec1.jpg"
            ]
        }
    },
    {
        "product_id": "airpods-pro",
        "name": "AirPods Pro",
        "category": "Earbuds",
        "attributes": {
            "price": 249,
            "weight": 56,
            "battery_life": 6,
            "noise_cancellation": 90,
            "material": "Plastic",
            "build_quality": "Good",
            "driver_type": "Custom high-excursion",
            "noise_cancellation_level": "Active",
            "clamp_force": 0,
            "padding_material": "Silicone tips",
            "foldability": True,
            "case_size": "Small",
            "usage_context": ["travel", "gym", "commute", "work"]
        },
        "visual_assets": {
            "main_image": "https://example.com/airpods-pro-main.jpg",
            "detail_images": [
                "https://example.com/airpods-pro-detail1.jpg"
            ],
            "spec_callouts": [
                "https://example.com/airpods-pro-spec1.jpg"
            ]
        }
    },
    {
        "product_id": "sony-wh1000xm5",
        "name": "Sony WH-1000XM5",
        "category": "Headphones",
        "attributes": {
            "price": 399,
            "weight": 250,
            "battery_life": 30,
            "noise_cancellation": 98,
            "material": "Plastic",
            "build_quality": "Excellent",
            "driver_type": "30mm",
            "noise_cancellation_level": "Active",
            "clamp_force": 3.8,
            "padding_material": "Protein leather",
            "foldability": True,
            "case_size": "Medium",
            "usage_context": ["travel", "home", "office", "commute"]
        },
        "visual_assets": {
            "main_image": "https://example.com/sony-wh1000xm5-main.jpg",
            "detail_images": [
                "https://example.com/sony-wh1000xm5-detail1.jpg"
            ],
            "spec_callouts": [
                "https://example.com/sony-wh1000xm5-spec1.jpg"
            ]
        }
    }
]


def seed_database():
    """Seed the database with sample products."""
    db = SessionLocal()
    service = ProductService()
    
    try:
        print("Seeding database with sample products...")
        
        for product_data in SAMPLE_PRODUCTS:
            # Check if product already exists
            existing = service.get_product_by_id(db, product_data["product_id"])
            if existing:
                print(f"Product {product_data['product_id']} already exists, skipping...")
                continue
            
            # Create product
            product_create = ProductCreate(**product_data)
            product = service.create_product(db, product_create)
            print(f"Created product: {product.name} ({product.product_id})")
        
        print("\nDatabase seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

