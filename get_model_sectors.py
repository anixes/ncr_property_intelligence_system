import sys
import asyncio
import pandas as pd

sys.path.append('.')

from ncr_property_price_estimation import state

async def get_sectors():
    await state.load_institutional_state()
    model = state.models.get('sales')
    if not model: return
    
    geo = model.named_steps.get('geo_encoder')
    if not geo: return
    
    # Filter for Noida to see what it actually has
    noida_df = geo.sec_stats_[geo.sec_stats_['city'] == 'Noida'].copy()
    
    # Sort by 'median_price' or 'count' if available in geo attributes
    # The geo_encoder stores these in .sec_stats_
    noida_df = noida_df.sort_values(by='geo_median', ascending=False)
    
    print("--- MODEL NOIDA SECTORS (TOP TIER) ---")
    print(noida_df[['sector', 'geo_median']].head(10).to_string(index=False))
    
    print("\n--- MODEL NOIDA SECTORS (MID TIER) ---")
    print(noida_df[['sector', 'geo_median']].iloc[20:30].to_string(index=False))
    
    print(f"\nTotal Sectors for Noida in Model: {len(noida_df)}")

if __name__ == "__main__":
    asyncio.run(get_sectors())
