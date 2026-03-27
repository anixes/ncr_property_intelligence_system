import pandas as pd
import numpy as np
import re
from pathlib import Path
from ncr_property_price_estimation.data.schema import PROPERTY_SCHEMA
import pandera as pa

# --- SETUP ---
PROJECT_ROOT = Path("d:/DATA SCIENCE/ncr_property_price_estimation")
INPUT_FILE = PROJECT_ROOT / "data/raw/final_ncr_properties.csv"

def run_diagnostic_eda():
    print(f"🕵️ DIAGNOSTIC EDA: Investigating 16,000+ Rejections...")
    df_raw = pd.read_csv(INPUT_FILE)
    
    # We re-run the PRE-VALIDATION step of the preprocessor to get the 'Full attempt'
    from ncr_property_price_estimation.data.preprocess_housing import HousingPreprocessor
    hp = HousingPreprocessor()
    
    # 1. Normalize as per current logic
    df = df_raw.copy()
    df['listing_mode'] = df['listing_type'].str.lower()
    df['price'] = df.apply(lambda r: hp.parse_price(str(r['price_text']), r['listing_mode']), axis=1)
    df['area'] = df['area_text'].apply(hp.parse_area)
    df['bedrooms'] = df['bhk'].apply(lambda x: int(re.search(r'\d+', str(x)).group(0)) if re.search(r'\d+', str(x)) else 0)
    df['bathrooms'] = df['bedrooms']
    df['balcony'] = 1
    df['locality'] = df['city']
    df['price_per_sqft'] = df['price'] / df['area']
    
    # 2. Identify Rows failing the Schema
    print(">> Capturing Schema Error Samples...")
    try:
        PROPERTY_SCHEMA.validate(df, lazy=True)
        print("Wait... No errors found? Something is wrong.")
    except pa.errors.SchemaErrors as e:
        failures = e.failure_cases
        print(f"\n📢 TOP REJECTION REASONS:")
        print(failures.groupby(['column', 'check']).size().sort_values(ascending=False).head(10))
        
        # 3. Inspect 'Price' failures specifically
        price_fails = failures[failures['column'] == 'price']
        if not price_fails.empty:
            print("\n🔍 SAMPLE PRICE FAILURES (Raw vs Parsed):")
            idx = price_fails['index'].head(5)
            print(df_raw.loc[idx, ['price_text', 'listing_type']])
            print(f"Parsed as: {df.loc[idx, 'price'].tolist()}")
            
        # 4. Inspect 'Area' failures specifically
        area_fails = failures[failures['column'] == 'area']
        if not area_fails.empty:
            print("\n🔍 SAMPLE AREA FAILURES (Raw vs Parsed):")
            idx = area_fails['index'].head(5)
            print(df_raw.loc[idx, ['area_text']])
            print(f"Parsed as: {df.loc[idx, 'area'].tolist()}")

if __name__ == "__main__":
    run_diagnostic_eda()
