"""Script to update database from XLSX file with multiple sheets."""
import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pandas as pd
except ImportError:
    print("Installing pandas and openpyxl...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    import pandas as pd

from src.database import SessionLocal, engine, Base
from src.models.product import Product, ProductAttribute, VisualAsset
from src.schemas.product import ProductCreate
from src.data.product_service import ProductService
import json

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


def parse_xlsx(xlsx_path):
    """Parse the XLSX file and extract data from all sheets."""
    print(f"Reading XLSX file: {xlsx_path}")
    
    # Read all sheets
    xlsx_file = pd.ExcelFile(xlsx_path)
    sheet_names = xlsx_file.sheet_names
    
    print(f"Found {len(sheet_names)} sheet(s): {', '.join(sheet_names)}")
    
    all_products = []
    intent_mappings = []
    
    for sheet_name in sheet_names:
        print(f"\nProcessing sheet: '{sheet_name}'")
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        
        # Display sheet info
        print(f"  Rows: {len(df)}, Columns: {df.columns.tolist()}")
        
        # Check if this is an intent mappings sheet
        if 'user_intent' in df.columns.str.lower().str.strip().tolist() or 'intent' in df.columns.str.lower().str.strip().tolist():
            # This looks like an intent mappings sheet
            mappings = parse_intent_mappings_sheet(df)
            intent_mappings.extend(mappings)
        elif sheet_name in ['Cause- Effect', 'Pre-Decision Intent']:
            # Intent mapping sheets
            mappings = parse_intent_mappings_sheet(df)
            intent_mappings.extend(mappings)
        elif sheet_name == 'Product MasterList':
            # Parse master list to create base products
            products = parse_master_list_sheet(df)
            if products:
                all_products.extend(products)
        else:
            # Try to parse as products sheet
            products = parse_products_sheet(df, sheet_name)
            if products:
                all_products.extend(products)
            else:
                print(f"  Could not parse sheet '{sheet_name}' - skipping")
    
    return all_products, intent_mappings


def parse_products_sheet(df, sheet_name):
    """Parse a products sheet and return list of product dictionaries."""
    products = []
    
    # Skip if too few rows
    if len(df) < 3:
        return products
    
    # Get product name from first row, first column
    product_name = str(df.iloc[0, 0]) if not pd.isna(df.iloc[0, 0]) else sheet_name
    product_name = product_name.split('-')[0].strip() if '-' in product_name else product_name.strip()
    
    # Find header row (usually row 2, index 2)
    header_row_idx = None
    for idx in range(min(5, len(df))):
        row_values = df.iloc[idx].astype(str).tolist()
        if 'variant_id' in row_values or 'product_id' in row_values:
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        print(f"  Warning: Could not find header row in sheet '{sheet_name}'")
        return products
    
    # Use header row as column names
    df.columns = df.iloc[header_row_idx].astype(str).str.strip()
    df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
    
    # Normalize column names (lowercase, strip spaces)
    df.columns = df.columns.str.lower().str.strip()
    
    # Find key columns
    variant_id_col = None
    product_id_col = None
    
    for col in df.columns:
        if 'variant_id' in col:
            variant_id_col = col
        if 'product_id' in col and variant_id_col is None:
            product_id_col = col
    
    # Process each data row (process ALL rows, don't skip based on empty variant_id)
    for idx, row in df.iterrows():
        # Check if this is an empty row (all values are NaN or empty)
        row_values = [v for v in row.values if not (pd.isna(v) or str(v).strip() == '')]
        if len(row_values) == 0:
            continue
        
        # Skip if variant_id is missing (but allow if product_id exists)
        if variant_id_col:
            variant_val = row.get(variant_id_col)
            if pd.isna(variant_val) or str(variant_val).strip() == '':
                # Check if product_id exists as fallback
                if product_id_col and not pd.isna(row.get(product_id_col)):
                    pass  # Continue with product_id
                else:
                    continue
        
        # Get variant/product ID
        if variant_id_col and not pd.isna(row.get(variant_id_col)):
            variant_id = str(row[variant_id_col]).strip()
            product_id = variant_id
        elif product_id_col and not pd.isna(row.get(product_id_col)):
            product_id = str(row[product_id_col]).strip()
        else:
            product_id = f"{sheet_name.lower().replace(' ', '-')}-{idx+1}"
        
        # Build product name with variant info
        name_parts = [product_name]
        if 'colorway' in df.columns and not pd.isna(row.get('colorway')):
            colorway = str(row['colorway']).strip()
            if colorway and colorway != 'nan' and colorway != '—':
                name_parts.append(colorway)
        name = ' '.join(name_parts)
        
        # Determine category from sheet name
        category = None
        if 'airpod' in sheet_name.lower() or 'headphone' in sheet_name.lower():
            category = 'Electronics'
        elif 'nike' in sheet_name.lower() or 'balance' in sheet_name.lower() or 'jordan' in sheet_name.lower():
            category = 'Footwear'
        elif 'vuitton' in sheet_name.lower() or 'gucci' in sheet_name.lower() or 'handbag' in sheet_name.lower() or 'bag' in sheet_name.lower():
            category = 'Handbag'
        else:
            category = sheet_name
        
        # Collect all columns as attributes
        attributes = {}
        visual_assets = {}
        
        for col in df.columns:
            value = row[col]
            
            # Skip NaN, empty, or dash values
            if pd.isna(value) or str(value).strip() in ['', '—', 'nan', 'NaN']:
                continue
            
            # Skip variant_id and product_id as attributes
            if col in [variant_id_col, product_id_col]:
                continue
            
            # Check if this is a visual asset column
            if 'image' in col.lower() or 'asset' in col.lower() or 'url' in col.lower():
                asset_type = 'main_image' if 'main' in col.lower() else 'detail_image'
                if asset_type not in visual_assets:
                    visual_assets[asset_type] = []
                visual_assets[asset_type].append(str(value))
            else:
                # It's an attribute
                attr_name = col.strip()
                
                # Convert value to appropriate type
                if isinstance(value, (int, float)) and not pd.isna(value):
                    attributes[attr_name] = value
                elif isinstance(value, bool):
                    attributes[attr_name] = value
                elif isinstance(value, str):
                    value_str = value.strip()
                    # Skip dash and empty
                    if value_str in ['—', '']:
                        continue
                    # Try to parse as number
                    try:
                        if '.' in value_str:
                            attributes[attr_name] = float(value_str)
                        else:
                            attributes[attr_name] = int(value_str)
                    except ValueError:
                        # Check if it's a list (comma-separated)
                        if ',' in value_str:
                            attributes[attr_name] = [v.strip() for v in value_str.split(',')]
                        else:
                            # Handle Yes/No as boolean
                            if value_str.lower() in ['yes', 'true', '1']:
                                attributes[attr_name] = True
                            elif value_str.lower() in ['no', 'false', '0']:
                                attributes[attr_name] = False
                            else:
                                attributes[attr_name] = value_str
                else:
                    attributes[attr_name] = str(value)
        
        # Create product dictionary
        product = {
            'product_id': product_id,
            'name': name,
            'category': category,
            'attributes': attributes,
            'visual_assets': visual_assets if visual_assets else {
                'main_image': f'https://example.com/{product_id}-main.jpg'
            }
        }
        
        products.append(product)
        print(f"  [OK] Parsed: {name} ({product_id})")
    
    return products


def parse_master_list_sheet(df):
    """Parse the Product MasterList sheet to create base products."""
    products = []
    
    # Find header row
    header_row_idx = None
    for idx in range(min(5, len(df))):
        row_values = [str(v).lower() if not pd.isna(v) else '' for v in df.iloc[idx].tolist()]
        if 'product_id' in ' '.join(row_values) and 'brand' in ' '.join(row_values):
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        print("  Warning: Could not find header row in Product MasterList")
        return products
    
    # Use header row as column names
    df.columns = df.iloc[header_row_idx].astype(str).str.strip()
    df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
    
    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Process each row
    for idx, row in df.iterrows():
        product_id = row.get('product_id')
        if pd.isna(product_id):
            continue
        
        product_id = str(product_id).strip()
        brand = str(row.get('brand', '')).strip() if not pd.isna(row.get('brand')) else ''
        model = str(row.get('model', '')).strip() if not pd.isna(row.get('model')) else ''
        category = str(row.get('category', '')).strip() if not pd.isna(row.get('category')) else ''
        sub_category = str(row.get('sub_category', '')).strip() if not pd.isna(row.get('sub_category')) else ''
        gender = str(row.get('gender', '')).strip() if not pd.isna(row.get('gender')) else ''
        base_price = row.get('base_price_usd')
        usage_context = str(row.get('usage_context', '')).strip() if not pd.isna(row.get('usage_context')) else ''
        
        # Build name
        name = f"{brand} {model}".strip() if brand and model else model or brand or product_id
        
        # Build attributes
        attributes = {}
        if brand:
            attributes['brand'] = brand
        if model:
            attributes['model'] = model
        if sub_category:
            attributes['sub_category'] = sub_category
        if gender:
            attributes['gender'] = gender
        if not pd.isna(base_price):
            try:
                attributes['base_price_usd'] = float(base_price)
            except:
                attributes['base_price_usd'] = str(base_price)
        if usage_context:
            # Parse comma-separated usage contexts
            contexts = [ctx.strip() for ctx in usage_context.split(',')]
            attributes['usage_context'] = contexts if len(contexts) > 1 else usage_context
        
        product = {
            'product_id': product_id,
            'name': name,
            'category': category,
            'attributes': attributes,
            'visual_assets': {
                'main_image': f'https://example.com/{product_id}-main.jpg'
            }
        }
        
        products.append(product)
        print(f"  [OK] Parsed base product: {name} ({product_id})")
    
    return products


def parse_intent_mappings_sheet(df):
    """Parse an intent mappings sheet."""
    mappings = []
    
    # Find header row
    header_row_idx = None
    for idx in range(min(5, len(df))):
        row_values = [str(val).lower() if not pd.isna(val) else '' for val in df.iloc[idx].tolist()]
        if any('user_intent' in val or ('intent' in val and 'response' not in val) for val in row_values):
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        print("  Warning: Could not find header row")
        return mappings
    
    # Use header row as column names
    df.columns = df.iloc[header_row_idx].astype(str).str.strip()
    df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
    
    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Find relevant columns
    intent_col = None
    product_type_col = None
    attributes_col = None
    response_type_col = None
    
    for col in df.columns:
        if 'user_intent' in col or ('intent' in col and 'response' not in col):
            intent_col = col
        if 'product_type' in col or ('type' in col and 'product' in col):
            product_type_col = col
        if 'matched_attribute' in col or ('attribute' in col and 'matched' in col):
            attributes_col = col
        if 'ai_response' in col or ('response' in col and 'type' in col):
            response_type_col = col
    
    if not intent_col:
        print("  Warning: Could not find intent column")
        return mappings
    
    for idx, row in df.iterrows():
        intent_val = row.get(intent_col)
        if pd.isna(intent_val) or str(intent_val).strip().lower() in ['user_intent', 'intent', '']:
            continue
        
        intent = str(intent_val).strip().strip('"').strip("'")
        # Skip header-like rows
        if intent.lower() in ['user_intent', 'intent', 'this is what you build logic on']:
            continue
        
        product_type = ""
        if product_type_col and not pd.isna(row.get(product_type_col)):
            product_type = str(row[product_type_col]).strip()
        
        attributes_str = ""
        if attributes_col and not pd.isna(row.get(attributes_col)):
            attributes_str = str(row[attributes_col]).strip().strip('"').strip("'")
        
        response_type = ""
        if response_type_col and not pd.isna(row.get(response_type_col)):
            response_type = str(row[response_type_col]).strip()
        
        attributes = [attr.strip() for attr in attributes_str.split(',')] if attributes_str and attributes_str.lower() not in ['matched_attributes', 'attributes'] else []
        
        mappings.append({
            'user_intent': intent,
            'product_type': product_type,
            'matched_attributes': attributes,
            'ai_response_type': response_type
        })
    
    return mappings


def seed_database_from_xlsx(xlsx_path):
    """Update database with data from XLSX file."""
    db = SessionLocal()
    service = ProductService()
    
    try:
        # Parse XLSX
        products, intent_mappings = parse_xlsx(xlsx_path)
        
        if not products:
            print("\n[WARNING] No products found in XLSX file!")
            return
        
        # Clear existing data
        print("\n" + "="*60)
        clear_database(db)
        
        # Create products
        print(f"\nCreating {len(products)} products...")
        created_count = 0
        seen_ids = set()
        
        for product_data in products:
            try:
                # Check for duplicate product IDs
                if product_data['product_id'] in seen_ids:
                    # Make it unique by appending sheet name or index
                    original_id = product_data['product_id']
                    counter = 1
                    while product_data['product_id'] in seen_ids:
                        product_data['product_id'] = f"{original_id}-{counter}"
                        counter += 1
                    print(f"  [WARN] Duplicate ID, using: {product_data['product_id']}")
                
                seen_ids.add(product_data['product_id'])
                product_create = ProductCreate(**product_data)
                product = service.create_product(db, product_create)
                created_count += 1
                print(f"  [OK] Created: {product.name} ({product.product_id})")
            except Exception as e:
                print(f"  [ERROR] Failed to create product {product_data.get('name', 'unknown')}: {e}")
                db.rollback()  # Rollback on error to continue with next product
        
        print(f"\n[SUCCESS] Database updated successfully!")
        print(f"  - Created {created_count} products")
        print(f"  - Found {len(intent_mappings)} intent mappings")
        
        if intent_mappings:
            print(f"\nIntent Mappings Summary:")
            for mapping in intent_mappings[:10]:  # Show first 10
                print(f"  - Intent: '{mapping['user_intent']}'")
                print(f"    Product Type: {mapping['product_type']}")
                print(f"    Attributes: {', '.join(mapping['matched_attributes'])}")
                print(f"    Response Type: {mapping['ai_response_type']}")
                print()
            if len(intent_mappings) > 10:
                print(f"  ... and {len(intent_mappings) - 10} more mappings")
        
    except Exception as e:
        print(f"[ERROR] Error updating database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    xlsx_path = os.path.join(os.path.dirname(__file__), '..', 'Product Attributes- Phase 3 Akari.xlsx')
    
    if not os.path.exists(xlsx_path):
        print(f"[ERROR] XLSX file not found: {xlsx_path}")
        sys.exit(1)
    
    seed_database_from_xlsx(xlsx_path)

