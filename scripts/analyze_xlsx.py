"""Script to analyze XLSX file and count all products."""
import pandas as pd
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

xlsx_path = 'Product Attributes- Phase 3 Akari.xlsx'
xls = pd.ExcelFile(xlsx_path)

print(f"Analyzing: {xlsx_path}")
print(f"Total sheets: {len(xls.sheet_names)}\n")

total_products = 0

for sheet_name in xls.sheet_names:
    if sheet_name in ['Product MasterList', 'Cause- Effect', 'Pre-Decision Intent']:
        continue
    
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None)
    
    # Find header row
    header_row = None
    for idx in range(min(5, len(df))):
        row_vals = [str(v).lower() if not pd.isna(v) else '' for v in df.iloc[idx].tolist()]
        if 'variant_id' in ' '.join(row_vals) or 'product_id' in ' '.join(row_vals):
            header_row = idx
            break
    
    if header_row is None:
        print(f"{sheet_name}: Could not find header row")
        continue
    
    # Count data rows
    data_rows = len(df) - header_row - 1
    print(f"{sheet_name}: {data_rows} products")
    
    # Show product IDs
    if header_row + 1 < len(df):
        df_data = df.iloc[header_row + 1:].copy()
        df_data.columns = df.iloc[header_row].astype(str).str.strip()
        
        variant_col = None
        for col in df_data.columns:
            if 'variant_id' in str(col).lower():
                variant_col = col
                break
        
        if variant_col:
            variants = df_data[variant_col].dropna().tolist()
            print(f"  Variants: {variants}")
        else:
            print(f"  (no variant_id column)")
    
    total_products += data_rows
    print()

print(f"Total products expected: {total_products}")

