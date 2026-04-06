import sys
import asyncio
import pandas as pd
import numpy as np

sys.path.append('.')

from ncr_property_price_estimation import state

async def debug():
    await state.load_institutional_state()
    m = state.models.get('sales')
    if not m:
        print("ERROR: Sales model not found.")
        return
    
    # Check Price Differentiation
    def get_price(s):
        try:
            df = pd.DataFrame([{
                'city': 'Noida',
                'sector': s,
                'area': 1800,
                'bedrooms': 3,
                'bathrooms': 3,
                'society': 'Unknown',
                'prop_type': 'Apartment',
                'amenities': {},
                'location_score': {},
                'features': {}
            }])
            return np.expm1(m.predict(df))[0]
        except Exception as e:
            return f"Error: {e}"

    print("\n--- PRICE DIFFERENTIATION TEST ---")
    p137 = get_price("Sector 137")
    p62 = get_price("Sector 62")
    p150 = get_price("Sector 150")  # This is missing in model, should equal p62/city avg
    
    print(f"Sector 137 (Premium):  ₹{p137:,.0f}" if isinstance(p137, float) else p137)
    print(f"Sector 62 (Standard):  ₹{p62:,.0f}" if isinstance(p62, float) else p62)
    print(f"Sector 150 (Missing):  ₹{p150:,.0f}" if isinstance(p150, float) else p150)
    
    if isinstance(p137, float) and isinstance(p62, float):
        print(f"Delta (137 vs 62):    ₹{abs(p137-p62):,.0f}")
    
    # Check Model Steps
    try:
        geo = m.named_steps.get('geo_encoder')
        if geo:
            sec_df = geo.sec_stats_
            noida_sec = sec_df[sec_df['city'] == 'Noida']['sector'].unique()
            print(f"\nSectors in Model: {len(noida_sec)}")
            print(f"Is 'Sector 150' in model? {'Sector 150' in noida_sec}")
            print(f"Is 'Sector 137' in model? {'Sector 137' in noida_sec}")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(debug())
