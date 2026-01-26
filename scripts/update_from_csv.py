"""Script to update database from CSV file with intent mappings and create sample products."""
import sys
import os
import csv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, engine, Base
from src.models.product import Product, ProductAttribute, VisualAsset
from src.schemas.product import ProductCreate
from src.data.product_service import ProductService

# Create tables
Base.metadata.create_all(bind=engine)


def clear_database(db):
    """Clear all existing data from the database."""
    print("Clearing existing database...")
    try:
        # Delete all visual assets
        db.query(VisualAsset).delete()
        # Delete all product attributes
        db.query(ProductAttribute).delete()
        # Delete all products
        db.query(Product).delete()
        db.commit()
        print("Database cleared successfully!")
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
        raise


def parse_csv(csv_path):
    """Parse the CSV file and extract intent mappings and product types."""
    intent_mappings = []
    product_types = set()
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                # Skip header rows (first 3 lines based on the file structure)
                for _ in range(3):
                    next(f, None)
                
                reader = csv.DictReader(f)
                for row in reader:
                    user_intent = row.get('user_intent', '').strip().strip('"').strip("'")
                    product_type = row.get('product_type', '').strip()
                    matched_attributes = row.get('matched_attributes', '').strip().strip('"').strip("'")
                    ai_response_type = row.get('AI_response_type', '').strip()
                    
                    if not user_intent or user_intent == '':
                        continue
                    
                    if product_type:
                        product_types.add(product_type)
                    
                    # Parse attributes
                    attrs = []
                    if matched_attributes:
                        attrs = [attr.strip() for attr in matched_attributes.split(',')]
                    
                    intent_mappings.append({
                        'user_intent': user_intent,
                        'product_type': product_type,
                        'matched_attributes': attrs,
                        'ai_response_type': ai_response_type
                    })
            
            # If we got here, parsing was successful
            break
        except (UnicodeDecodeError, KeyError) as e:
            if encoding == encodings[-1]:
                # Last encoding failed, raise error
                raise Exception(f"Failed to parse CSV with all encodings. Last error: {e}")
            continue
    
    return intent_mappings, product_types


def create_sample_products(product_types):
    """Create sample products based on product types from CSV."""
    products = []
    
    # Sample products for each type
    product_templates = {
        'Electronics': {
            'product_id': 'electronics-sample-1',
            'name': 'Premium Wireless Headphones',
            'category': 'Electronics',
            'attributes': {
                'weight': 350,  # grams
                'cushioning': 'Memory foam',
                'material': 'Aluminum and leather',
                'durability': 'High',
                'price': 299,
                'battery_life': 30,
                'noise_cancellation': True
            },
            'visual_assets': {
                'main_image': 'https://example.com/electronics-main.jpg'
            }
        },
        'Footwear / Bag': {
            'product_id': 'footwear-bag-sample-1',
            'name': 'Comfortable Walking Shoes',
            'category': 'Footwear',
            'attributes': {
                'colorway': 'Black, White, Gray',
                'cushioning': 'Gel cushioning',
                'sole': 'Rubber sole with arch support',
                'weight': 280,  # grams per shoe
                'material': 'Mesh and synthetic',
                'durability': 'Medium-High'
            },
            'visual_assets': {
                'main_image': 'https://example.com/footwear-main.jpg'
            }
        },
        'Handbag': {
            'product_id': 'handbag-sample-1',
            'name': 'Designer Leather Handbag',
            'category': 'Handbag',
            'attributes': {
                'weight': 850,  # grams
                'material': 'Genuine leather',
                'colorway': 'Brown, Black, Tan',
                'durability': 'High',
                'price': 450,
                'size': 'Medium'
            },
            'visual_assets': {
                'main_image': 'https://example.com/handbag-main.jpg'
            }
        },
        'Footwear': {
            'product_id': 'footwear-sample-1',
            'name': 'Running Shoes',
            'category': 'Footwear',
            'attributes': {
                'cushioning': 'Air cushioning',
                'sole': 'Lightweight EVA sole',
                'colorway': 'Blue, Red, White',
                'weight': 250,  # grams per shoe
                'material': 'Breathable mesh',
                'durability': 'High'
            },
            'visual_assets': {
                'main_image': 'https://example.com/running-shoes-main.jpg'
            }
        }
    }
    
    # Create products for each unique product type
    for product_type in product_types:
        if product_type == 'All':
            # For "All" type, create a generic product
            products.append({
                'product_id': 'generic-product-1',
                'name': 'Generic Product',
                'category': 'General',
                'attributes': {
                    'material': 'Various',
                    'durability': 'Medium',
                    'price': 100
                },
                'visual_assets': {
                    'main_image': 'https://example.com/generic-main.jpg'
                }
            })
        elif product_type in product_templates:
            products.append(product_templates[product_type])
        else:
            # Create a generic product for unknown types
            products.append({
                'product_id': f'{product_type.lower().replace(" ", "-")}-sample-1',
                'name': f'Sample {product_type}',
                'category': product_type,
                'attributes': {
                    'material': 'Standard',
                    'durability': 'Medium'
                },
                'visual_assets': {
                    'main_image': f'https://example.com/{product_type.lower().replace(" ", "-")}-main.jpg'
                }
            })
    
    return products


def seed_database_from_csv(csv_path):
    """Update database with data from CSV file."""
    db = SessionLocal()
    service = ProductService()
    
    try:
        # Parse CSV
        print(f"Reading CSV file: {csv_path}")
        intent_mappings, product_types = parse_csv(csv_path)
        
        print(f"\nFound {len(intent_mappings)} intent mappings")
        print(f"Product types: {', '.join(product_types)}")
        
        # Clear existing data
        clear_database(db)
        
        # Create sample products
        products = create_sample_products(product_types)
        print(f"\nCreating {len(products)} products...")
        
        for product_data in products:
            product_create = ProductCreate(**product_data)
            product = service.create_product(db, product_create)
            print(f"  [OK] Created: {product.name} ({product.product_id})")
        
        print(f"\n[SUCCESS] Database updated successfully!")
        print(f"\nIntent Mappings Summary:")
        for mapping in intent_mappings:
            print(f"  - Intent: '{mapping['user_intent']}'")
            print(f"    Product Type: {mapping['product_type']}")
            print(f"    Attributes: {', '.join(mapping['matched_attributes'])}")
            print(f"    Response Type: {mapping['ai_response_type']}")
            print()
        
    except Exception as e:
        print(f"[ERROR] Error updating database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'Product Attributes- Phase 3 Akari - Pre-Decision Intent.csv')
    
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        sys.exit(1)
    
    seed_database_from_csv(csv_path)

