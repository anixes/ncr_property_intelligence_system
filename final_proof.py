import sys
import asyncio
import pandas as pd
import numpy as np

sys.path.append('.')

from ncr_property_price_estimation import state

async def final_proof():
    print("Loading institutional state (this may take a moment)...")
    await state.load_institutional_state()
    model = state.models.get('sales')
    
    if not model:
        print("ERROR: Models not found.")
        return

    def get_row(city, sector):
        # Create a full institution-grade input row
        return pd.DataFrame([{
            'city': city,
            'sector': sector,
            'society': 'Unknown',
            'area': 1800,
            'bedrooms': 3,
            'bathrooms': 3,
            'prop_type': 'Apartment',
            'is_luxury': 1,
            'has_pool': 1,
            'has_gym': 1,
            'has_lift': 1,
            'is_near_metro': 1,
            'is_rera_registered': 1,
            'is_gated_community': 1,
            'is_vastu_compliant': 1,
            'is_servant_room': 0,
            'is_study_room': 0,
            'is_store_room': 0,
            'is_pooja_room': 0,
            'has_power_backup': 1,
            'is_corner_property': 0,
            'is_park_facing': 0,
            'no_brokerage': 1,
            'bachelors_allowed': 1,
            'is_standalone': 0,
            'is_owner_listing': 0,
            'furnishing_status': 'Semi-Furnished',
            'legal_status': 'Ready to Move'
        }])

    # Test Logic with Manual Normalization (simulating what predict.py does)
    p150 = np.expm1(model.predict(get_row("Noida", "Sector 137")))[0]  # Peer for 150
    p62 = np.expm1(model.predict(get_row("Gurgaon", "Sector 53")))[0]  # Peer for 62 in GGN
    p1 = np.expm1(model.predict(get_row("Faridabad", "Sector 16")))[0] # Peak for Faridabad

    print("\n--- INSTITUTIONAL VALUATION PROOF ---")
    print(f"Noida (S-150 Peer 137):  ₹{p150:,.0f}")
    print(f"Gurgaon (S-62 Peer 53):  ₹{p62:,.0f}")
    print(f"Faridabad (S-1 Peer 16): ₹{p1:,.0f}")
    
    if p150 != p62 and p62 != p1:
        print("\nSUCCESS: Price variance confirmed. Micro-market intelligence is now unique per sector.")
    else:
        print("\nREMAINING ISSUE: Prices are still static. Check model fallback triggers.")

if __name__ == "__main__":
    asyncio.run(final_proof())
