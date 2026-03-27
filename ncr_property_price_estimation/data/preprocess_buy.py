import pandas as pd
import numpy as np
import re
from pathlib import Path
from ncr_property_price_estimation.data.schema import validate_dataframe
from ncr_property_price_estimation.data.validator import ValidationService

# --- CONFIGURATION ---
PROJECT_ROOT = Path("d:/DATA SCIENCE/ncr_property_price_estimation")
INPUT_FILE = PROJECT_ROOT / "data/raw/raw_ncr_buy.csv"
OUTPUT_FILE = PROJECT_ROOT / "data/interim/sales_cleaned.parquet"

class BuyPreprocessor:
    """Specialized Preprocessor for Sale Data (V19.7)"""
    
    def __init__(self):
        self.validator = ValidationService()
        
    def parse_price(self, text):
        """Mega-Recovery Price Parser (V19.8) - Deep Extraction."""
        if not isinstance(text, str): return np.nan
        text = text.replace(',', '').strip()
        
        # 1. Primary: Look for Cr/L/K patterns (Standard)
        match_cr_l = re.search(r"(\d+\.?\d*)\s*(Cr|L|K|Lakh|Crore|Million)", text, re.IGNORECASE)
        if match_cr_l:
            try:
                val = float(match_cr_l.group(1))
                unit = match_cr_l.group(2).lower()
                if 'cr' in unit or 'crore' in unit: val *= 10000000
                elif 'l' in unit or 'lakh' in unit: val *= 100000
                elif 'k' in unit or 'million' in unit: val *= 1000 if 'k' in unit else 1000000
                return val
            except: pass
            
        # 2. Backup: Look for plain numbers with ₹ symbol
        match_plain = re.search(r"₹\s*(\d+)", text)
        if match_plain:
            return float(match_plain.group(1))
            
        return np.nan

    def parse_area(self, text):
        """Mega-Recovery Area Parser (V19.8) - Deep Extraction & Unit Conv."""
        if not isinstance(text, str): return np.nan
        text_clean = text.replace(',', '').lower()
        
        # 1. Primary: Standard sq.ft
        match_sqft = re.search(r"(\d+)\s*(sq\.ft|sqft|sq-ft|square\s*feet|super\s*area)", text_clean)
        if match_sqft:
            return float(match_sqft.group(1))
            
        # 2. Secondary: Yard Conversion (1 Yard = 9 Sqft)
        match_yards = re.search(r"(\d+)\s*(sq\.\s*yards?|sqrd|sq\s*yd|yards?)", text_clean)
        if match_yards:
            val = float(match_yards.group(1))
            if val < 1000: # Heuristic: If it's 1200 it's already sqft, if it's 200 it's likely yards
                return val * 9
            return val
            
        return np.nan

    def extract_nlp_features(self, df):
        """Flags amenities and USPs from raw descriptions."""
        desc = df['description_raw'].fillna('').str.lower()
        
        df['ready_to_move'] = desc.str.contains('ready to move|possession status').astype('Int64')
        df['is_luxury'] = desc.str.contains('luxury|premium|ultra|high-end').astype('Int64')
        df['is_gated_community'] = desc.str.contains('gated|security|24\*7').astype('Int64')
        df['is_vastu_compliant'] = desc.str.contains('vastu|vatu').astype('Int64')
        
        # Physical Attributes
        df['has_pool'] = desc.str.contains('pool|swimming').astype('Int64')
        df['has_gym'] = desc.str.contains('gym|fitness').astype('Int64')
        df['has_lift'] = desc.str.contains('lift|elevator').astype('Int64')
        
        return df

    def run(self):
        print(f"🏠 PROCESSING SALES: {INPUT_FILE}")
        df = pd.read_csv(INPUT_FILE)
        
        df['listing_mode'] = 'buy'
        
        # New V19.8 Step: Deep Merge of Price/Area from text blobs
        print(">> Deep Mining Price & Area from Raw Text blocks...")
        df['price'] = df.apply(lambda r: self.parse_price(str(r['price_text'])) or self.parse_price(str(r['description_raw'])), axis=1)
        df['area'] = df.apply(lambda r: self.parse_area(str(r['area_text'])) or self.parse_area(str(r['description_raw'])), axis=1)
        
        # BHK integer extraction
        df['bedrooms'] = df['bhk_text'].apply(lambda x: int(re.search(r'\d+', str(x)).group(0)) if re.search(r'\d+', str(x)) else 1)
        df['bathrooms'] = df['bedrooms']
        df['balcony'] = 1
        
        # Features
        df = self.extract_nlp_features(df)
        df['society_name'] = df['society_hint'].fillna('Independent')
        df['locality'] = df['city']
        def get_sector(title):
            m = re.search(r'Sector\s*(\d+[A-Z]?)', str(title), re.I)
            return f"Sector {m.group(1)}" if m else None
            
        df['sector'] = df['title_raw'].apply(get_sector)
        
        # Agent/Owner Features
        df['agent_name'] = df.get('agent_name', 'Unknown')
        df['is_individual'] = df['agent_name'].str.contains('Owner|Individual', case=False, na=False).astype(int)
        
        # Validation (Price >= 5L as per current schema)
        df = df.dropna(subset=['price', 'area'])
        df['price_per_sqft'] = df['price'] / df['area']
        df = df.dropna(subset=['price_per_sqft'])
        
        clean_df, stats = validate_dataframe(df)
        clean_df.to_parquet(OUTPUT_FILE, index=False)
        print(f"✅ SALE SUCCESS: Saved {len(clean_df)} records. Yield: {stats['valid_rows'] / stats['total_rows'] * 100:.1f}%")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append("d:/DATA SCIENCE/ncr_property_price_estimation")
    BuyPreprocessor().run()
