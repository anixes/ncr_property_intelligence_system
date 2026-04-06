import sys
import asyncio
import pandas as pd

sys.path.append('.')

from ncr_property_price_estimation import state

async def get_vocabulary():
    await state.load_institutional_state()
    model = state.models.get('sales')
    if not model: return
    
    geo = model.named_steps.get('geo_encoder')
    if not geo: return
    
    # Get all sectors the model knows
    noida_sectors = geo.sec_stats_[geo.sec_stats_['city'] == 'Noida']['sector'].unique().tolist()
    print("MODEL_NOIDA_VOCABULARY = " + str(noida_sectors))

if __name__ == "__main__":
    asyncio.run(get_vocabulary())
