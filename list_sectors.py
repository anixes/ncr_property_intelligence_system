import sys
import asyncio
import pandas as pd

sys.path.append('.')

from ncr_property_price_estimation import state

async def list_sectors():
    await state.load_institutional_state()
    model = state.models.get('sales')
    if not model:
        print("Models not found.")
        return
    
    geo = model.named_steps.get('geo_encoder')
    if geo:
        sectors = geo.sec_stats_['sector'].unique().tolist()
        # Filter for Noida sectors to keep it relevant
        noida_sectors = [s for s in sectors if "sector" in s.lower()]
        print("LEGITIMATE SECTORS IN MODEL (Noida Samples):")
        print(noida_sectors[:30])
    else:
        print("Geo encoder not found in pipeline.")

if __name__ == "__main__":
    asyncio.run(list_sectors())
