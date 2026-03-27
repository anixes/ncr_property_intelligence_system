import pandas as pd
import json
from pathlib import Path

def build_index():
    root_dir = Path(__file__).parent.parent
    data_path = root_dir / "Full_Audit_NCR.csv"
    output_path = root_dir / "locality_intelligence_index.json"
    
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, usecols=['city', 'locality', 'price', 'area', 'listing_type', 'society_name'])
    
    # Clean locality
    df['locality'] = df['locality'].fillna('Other')
    
    # Calculate price per sqft
    df['price_sqft'] = df['price'] / df['area']
    # Filter out extreme outliers (data quality)
    df = df[(df['price_sqft'] > 10) & (df['price_sqft'] < 100000)].copy()

    # Normalize city names for UI matching
    city_map = {
        "Gurgaon": "Gurugram",
        "Greater_Noida": "Greater Noida"
    }
    df['ui_city'] = df['city'].apply(lambda c: city_map.get(str(c), str(c)))

    # Separate Buy and Rent data
    buy_df = df[df['listing_type'] == 'Buy']
    rent_df = df[df['listing_type'] == 'Rent']
    
    index = {}
    
    grouped = df.groupby(['ui_city', 'locality'])
    for (city, loc), group in grouped:
        if city not in index:
            index[city] = {}
        
        # Get Buy & Rent price_sqft medians
        loc_buy = buy_df[(buy_df['ui_city'] == city) & (buy_df['locality'] == loc)]
        loc_rent = rent_df[(rent_df['ui_city'] == city) & (rent_df['locality'] == loc)]
        
        median_price_sqft = loc_buy['price_sqft'].median() if not loc_buy.empty else 0
        median_rent_sqft = loc_rent['price_sqft'].median() if not loc_rent.empty else 0
        
        median_price_sqft = float(median_price_sqft) if pd.notna(median_price_sqft) else 0.0
        median_rent_sqft = float(median_rent_sqft) if pd.notna(median_rent_sqft) else 0.0
        
        # Gross Rental Yield
        # (rent per sqft * 12) / price per sqft
        gross_yield = 0.0
        if median_price_sqft > 0 and median_rent_sqft > 0:
            gross_yield = (median_rent_sqft * 12) / median_price_sqft * 100.0
            
        # Top Societies
        societies = group['society_name'].dropna().value_counts()
        # Filter generic
        valid_socs = []
        for soc in societies.index:
            s_low = soc.lower()
            if not any(x in s_low for x in ['independent', 'standalone', 'other', 'unknown', 'nan', 'block ']):
                valid_socs.append(soc)
            if len(valid_socs) >= 5:
                break
                
        index[city][loc] = {
            "median_price_sqft": round(median_price_sqft, 2),
            "median_rent_sqft": round(median_rent_sqft, 2),
            "gross_yield_pct": round(gross_yield, 2),
            "listing_count": len(group),
            "top_societies": valid_socs
        }
    
    with open(output_path, 'w') as f:
        json.dump(index, f, indent=2)
    print(f"Index built with {len(index)} cities and saved to {output_path}.")

if __name__ == "__main__":
    build_index()
