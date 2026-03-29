import pandas as pd
import numpy as np
import re
from pathlib import Path
from ncr_property_price_estimation.config import PROJ_ROOT, RAW_DATA_DIR
from ncr_property_price_estimation.data.schema import validate_dataframe
from ncr_property_price_estimation.data.validator import ValidationService

# --- CONFIGURATION ---
INPUT_FILE = RAW_DATA_DIR / "raw_ncr_buy.csv"
OUTPUT_FILE = PROJ_ROOT / "data" / "interim" / "sales_cleaned.parquet"

class BuyPreprocessor:
    """Specialized Preprocessor for Rental Data"""
    
    def __init__(self):
        self.validator = ValidationService()
        
    def parse_price(self, text):
        """Mega-Recovery Price Parser - Deep Extraction."""
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
        """Mega-Recovery Area Parser - Deep Extraction."""
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
        """Flags amenities, USPs, and furnishing from raw descriptions."""
        desc = df['description_raw'].fillna('').str.lower()
        title = df['title_raw'].fillna('').str.lower()
        combined = desc + " | " + title
        
        df['ready_to_move'] = desc.str.contains('available now|ready to move|immediate|possession status').astype(int)
        df['is_luxury'] = desc.str.contains('luxury|premium|ultra|high-end|posh').astype(int)
        df['is_gated_community'] = desc.str.contains('gated|security|24\*7').astype(int)
        df['is_vastu_compliant'] = desc.str.contains('vastu|vatu').astype(int)
        
        # Physical Attributes
        df['has_pool'] = desc.str.contains('pool|swimming').astype(int)
        df['has_gym'] = desc.str.contains('gym|fitness').astype(int)
        df['has_lift'] = desc.str.contains('lift|elevator').astype(int)
        
        # FURNISHING Status
        def get_furnishing(txt):
            if re.search(r'fully|full[- ]?furnished', txt): return 'Fully-Furnished'
            if re.search(r'semi[- ]?furnished', txt): return 'Semi-Furnished'
            if re.search(r'unfurnished', txt): return 'Unfurnished'
            return 'Semi-Furnished' # NCR Default
            
        df['furnishing_status'] = combined.apply(get_furnishing)
        
        # Premium NLP Flags
        df['is_near_metro'] = combined.str.contains(r'metro').astype(int)
        df['has_power_backup'] = combined.str.contains(r'power backup').astype(int)
        df['is_corner_property'] = combined.str.contains(r'corner').astype(int)
        df['is_park_facing'] = combined.str.contains(r'park facing|green facing|park view|green view').astype(int)
        df['no_brokerage'] = combined.str.contains(r'no brokerage|zero brokerage').astype(int)
        df['bachelors_allowed'] = combined.str.contains(r'bachelor').astype(int)
        
        # Missing Data Propagation
        valid_text_mask = combined.str.len() > 15
        
        nlp_binary_cols = [
            'ready_to_move', 'is_luxury', 'is_gated_community', 'is_vastu_compliant',
            'has_pool', 'has_gym', 'has_lift', 'is_near_metro',
            'has_power_backup', 'is_corner_property', 'is_park_facing', 'no_brokerage',
            'bachelors_allowed'
        ]
        
        for col in nlp_binary_cols:
            if col in df.columns:
                df[col] = df[col].astype(float).where(valid_text_mask, np.nan)
        
        return df

    def run(self):
        print(f"🏠 PROCESSING SALES: {INPUT_FILE}")
        df = pd.read_csv(INPUT_FILE)
        
        df['listing_mode'] = 'buy'
        
        # Deep Merge of Price/Area from text blobs
        print(">> Deep Mining Price & Area from Raw Text blocks...")
        df['price'] = df.apply(lambda r: self.parse_price(str(r['price_text'])) or self.parse_price(str(r['description_raw'])), axis=1)
        df['area'] = df.apply(lambda r: self.parse_area(str(r['area_text'])) or self.parse_area(str(r['description_raw'])), axis=1)
        
        # ROOM EXTRACTION (Robust Rooms) ported from Rent
        def extract_rooms(row):
            title = str(row.get('title_raw', '')).lower()
            desc = str(row.get('description_raw', '')).lower()
            combined = f"{title} | {desc}"
            
            bhk = None
            m_bhk = re.search(r'(\d+(?:\.\d+)?)\s*(?:bhk|bedroom|bed room)', title)
            if m_bhk:
                bhk = float(m_bhk.group(1))
            else:
                m_bhk = re.search(r'(\d+(?:\.\d+)?)\s*(?:bhk|bedroom|bed room)', desc)
                if m_bhk:
                    bhk = float(m_bhk.group(1))
            
            if bhk is None:
                bhk_val = str(row.get('bhk_text', ''))
                m_tag = re.search(r'(\d+)', bhk_val)
                bhk = float(m_tag.group(1)) if m_tag else 1.0

            bedrooms = int(bhk)
            has_extra = 1 if (bhk % 1 == 0.5) else 0
            
            bathrooms = bedrooms
            m_bath = re.search(r'(\d+)\s*(?:bath|toilet|t\b)', combined)
            if m_bath:
                bathrooms = int(m_bath.group(1))
            
            if bathrooms > bedrooms + 2:
                bathrooms = bedrooms + 1
            
            is_servant = 1 if 'servant' in combined or ' sr ' in combined else 0
            is_study = 1 if 'study' in combined or ' st ' in combined or has_extra else 0
            is_store = 1 if 'store' in combined else 0
            is_pooja = 1 if 'pooja' in combined else 0
            
            return pd.Series({
                'bedrooms': bedrooms, 
                'bathrooms': bathrooms, 
                'balcony': 1, # default used in buy
                'is_servant_room': is_servant,
                'is_study_room': is_study,
                'is_store_room': is_store,
                'is_pooja_room': is_pooja
            })

        print(">> Extracting reconciled Bedroom/Bathroom counts...")
        rooms_df = df.apply(extract_rooms, axis=1)
        df = pd.concat([df, rooms_df], axis=1)
        
        # Features
        df = self.extract_nlp_features(df)
        
        # Property Type Extraction
        def get_prop_type(title):
            title = str(title).lower()
            if any(x in title for x in ['independent builder floor', 'builder floor', 'floor']):
                return 'Builder Floor'
            if any(x in title for x in ['house', 'villa', 'bungalow', 'kothi']):
                return 'House'
            if any(x in title for x in ['flat', 'apartment', 'penthouse']):
                return 'Apartment'
            if any(x in title for x in ['plot', 'land']):
                return 'Plot'
            return 'Apartment'

        df['prop_type'] = df['title_raw'].apply(get_prop_type)
        df['is_standalone'] = df['title_raw'].str.contains(r'Independent|Plot|House|Kothi|Villa|Bungalow', case=False, na=False).astype(int)

        # Sector extraction from title
        def get_sector(title):
            m = re.search(r'Sector\s*(\d+[A-Z]?)', str(title), re.I)
            return f"Sector {m.group(1)}" if m else None
        df['sector'] = df['title_raw'].apply(get_sector)

        def get_locality(row):
            title = str(row.get('title_raw', ''))
            city = str(row.get('city', ''))
            city_clean = city.replace('_', ' ')
            m = re.search(r'\bin\s+(.+?)(?:,\s*' + re.escape(city_clean) + r'|\s*$)', title, re.IGNORECASE)
            if m:
                loc = m.group(1).strip().rstrip(',')
                if loc and loc.lower() not in [city_clean.lower(), 'new delhi', 'delhi', '']:
                    return loc
            return city
        df['locality'] = df.apply(get_locality, axis=1)

        # --- REFINED EXTRACTION ---
        DEVELOPERS = [
            "M3M", "DLF", "Godrej", "Emaar", "IREO", "Vatika", "SS", "Bestech", 
            "Central Park", "Ambience", "Tulip", "AIPL", "Experion", "Puri", 
            "Signature", "Whiteland", "Elan", "Conscient", "Krisumi", "TATA", 
            "Adani", "Hemisphere", "Omaxe", "Piyush", "RPS", "Uppal", "Ireo"
        ]
        
        def extract_society_from_desc(desc, title):
            if not isinstance(desc, str) or not isinstance(title, str):
                return None
            lines = [l.strip() for l in desc.split('\n') if l.strip()]
            title_clean = title.strip().lower()
            for i, line in enumerate(lines):
                if line.lower() == title_clean:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        cand = lines[j].strip()
                        if cand.upper() == 'RERA' or len(cand) > 60:
                            break
                        
                        noise_words = [
                            '₹', 'sq.ft', 'sq-ft', 'sqft', 'price', 'builtup', 'plot area',
                            'verified', 'resale', 'new booking', 'ready to move', 'possession',
                            'highlights:', 'contact', 'updated', 'ago', 'rera', 'facing', 'independent'
                        ]
                        if any(x in cand.lower() for x in noise_words) or re.match(r'^[₹\d]', cand):
                            continue
                            
                        if len(cand) > 2:
                            return cand
            return None

        def refine_society_and_locality(row):
            title = str(row.get('title_raw', ''))
            desc = str(row.get('description_raw', ''))
            full_loc = str(row.get('locality', ''))
            city = str(row.get('city', ''))
            
            parts = [p.strip() for p in full_loc.split(',')]
            parts = [p for p in parts if p.lower() not in [city.lower(), 'delhi', 'new delhi', 'ncr']]
            
            desc_head = desc.split('\n')[0] if isinstance(desc, str) else ""
            combined_text = f"{title} | {desc_head}"
            
            society = None
            
            soc_desc = extract_society_from_desc(desc, title)
            if soc_desc:
                society = soc_desc
            
            if not society:
                for dev in DEVELOPERS:
                    m = re.search(r'\b(' + re.escape(dev) + r'\s+[a-z0-9]+(?:\s+[a-z0-9]+)?)\b', combined_text, re.I)
                    if m: 
                        society = m.group(1).strip()
                        break
            
            if not society:
                m = re.search(r'\b([a-z0-9\-]+\s+(?:[a-z0-9\-]+\s+)?(?:Heights|Residency|Greens|Solitude|Estate|Villas|Floors|Gardens|Park|City|Township|Elite|Classic|Avenue|Plaza|Casa|Gems|Jewel|Pearl|Square|Enclave))\b', combined_text, re.I)
                if m and not m.group(1).lower().endswith('real estate'):
                    society = m.group(1).strip()
            
            if society and society.isupper():
                society = society.title()
            
            if not society:
                for p in parts:
                    if re.match(r'^(block|pocket|phase|ward)\s+[R0-9A-Za-z-]+$', p.strip(), re.I) or p.strip().lower() in ['block', 'pocket', 'phase', 'ward']:
                        if 'sector' not in p.lower():
                            society = p
                            break
            
            if not society:
                if 'independent' in title.lower():
                    society = 'Independent'
            
            if not society and len(parts) > 1:
                if 'sector' not in parts[0].lower():
                    society = parts[0]
            
            if not society: society = "Standalone"
            
            locality = city
            for p in parts:
                p_lower = p.lower()
                is_generic = re.match(r'^(block|pocket|phase|ward)\s+[R0-9A-Za-z-]+$', p_lower) or p_lower in ['block', 'pocket', 'phase', 'ward']
                is_sector = 'sector' in p_lower
                
                if not is_generic and not is_sector and p.lower() != str(society).lower():
                    locality = p
                    break
            
            if locality == city:
                for p in parts:
                    if 'sector' in p.lower() and p.lower() != str(society).lower():
                        locality = p
                        break
            
            if locality == city and len(parts) > 0:
                for p in parts:
                    if p.lower() != str(society).lower():
                        locality = p
                        break
            
            return pd.Series({'soc_clean': society, 'loc_clean': locality})

        print(">> Extracting reconciled Society/Locality boundaries...")
        res = df.apply(refine_society_and_locality, axis=1)
        df['society_name'] = res['soc_clean']
        df['locality'] = res['loc_clean']

        # FINAL CONSISTENCY OVERRIDES
        df.loc[df['prop_type'] == 'Apartment', 'society_name'] = df.loc[df['prop_type'] == 'Apartment', 'society_name'].replace('Independent', 'Standalone')
        df.loc[(df['is_standalone'] == 1) & (df['society_name'] == 'Standalone'), 'society_name'] = 'Independent'

        # Agent Name Reconstruction
        def refine_agent(row):
            hint = str(row.get('society_hint', ''))
            desc = str(row.get('description_raw', ''))
            if len(hint) <= 3 and hint not in ['nan', '', 'None']:
                m = re.search(r'^' + re.escape(hint) + r'\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', desc)
                if m: return m.group(1).strip()
            return hint if hint != 'nan' else 'Unknown'

        df['agent_name'] = df.apply(refine_agent, axis=1)
        df['is_owner_listing'] = df['agent_name'].str.contains(r'Owner|Individual|None|A$|V$', case=False, na=False).astype(int)
        
        # Validation
        df = df.dropna(subset=['price', 'area'])
        df['price_per_sqft'] = df['price'] / df['area']
        df = df.dropna(subset=['price_per_sqft'])
        
        clean_df, stats = validate_dataframe(df)
        clean_df.to_parquet(OUTPUT_FILE, index=False)
        print(f"✅ SALE SUCCESS: Saved {len(clean_df)} records. Yield: {stats['valid_rows'] / stats['total_rows'] * 100:.1f}%")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(str(PROJ_ROOT))
    BuyPreprocessor().run()
