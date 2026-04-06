import sys
import asyncio
import pandas as pd

sys.path.append('.')

from ncr_property_price_estimation import state

async def get_multi_city_vocab():
    await state.load_institutional_state()
    model = state.models.get('sales')
    if not model: return
    
    geo = model.named_steps.get('geo_encoder')
    if not geo: return
    
    stats = geo.sec_stats_
    print(f"COLUMNS: {stats.columns.tolist()}")
    
    # Try common median columns
    target_col = next((c for c in ['geo_median', 'price_median', 'price', 'median'] if c in stats.columns), stats.columns[-1])
    
    for city in ['Gurgaon', 'Faridabad', 'Noida']:
        city_df = stats[stats['city'] == city].sort_values(by=target_col, ascending=False)
        print(f"\n--- {city.upper()} CIUSTERS ---")
        if len(city_df) > 0:
            print("PEERS:", city_df['sector'].head(3).tolist())
        else:
            print("No data.")

if __name__ == "__main__":
    asyncio.run(get_multi_city_vocab())
