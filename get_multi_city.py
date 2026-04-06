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
    
    cities = ['Gurgaon', 'Faridabad', 'Ghaziabad']
    for city in cities:
        city_df = geo.sec_stats_[geo.sec_stats_['city'] == city].sort_values(by='geo_median', ascending=False)
        print(f"\n--- {city.upper()} CLUSTERS ---")
        if len(city_df) > 0:
            print("PREMIUM PEER:", city_df.iloc[0]['sector'], f" (₹{city_df.iloc[0]['geo_median']:,.0f}/sqft)")
            if len(city_df) > 5:
                print("MID PEER:    ", city_df.iloc[len(city_df)//2]['sector'], f" (₹{city_df.iloc[len(city_df)//2]['geo_median']:,.0f}/sqft)")
                print("CENTRAL PEER:", city_df.iloc[-1]['sector'], f" (₹{city_df.iloc[-1]['geo_median']:,.0f}/sqft)")
        else:
            print("No data in model for this city.")

if __name__ == "__main__":
    asyncio.run(get_multi_city_vocab())
