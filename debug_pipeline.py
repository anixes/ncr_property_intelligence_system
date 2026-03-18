import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import os
import sys

# Ensure project root is in path
PROJ_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJ_ROOT))

from ncr_property_price_estimation.config import MODELS_DIR

# Load model
model_path = MODELS_DIR / "pipeline_v1.joblib"
if not model_path.exists():
    print(f"ERROR: Model not found at {model_path}")
    sys.exit(1)

print(f"Loading model from {model_path}")
pipeline = joblib.load(model_path)

# Test input (Gurugram, Sector 49, 1200 sqft, 3 BHK, 2 Bath)
test_input = {
    "area": 1200.0,
    "bedrooms": 3,
    "bathrooms": 2,
    "balcony": 2,
    "floor": 8,
    "prop_type": "Apartment",
    "furnished": "Unknown",
    "facing": "Unknown",
    "city": "Gurugram",
    "sector": "Sector 49",
    "pooja_room": 0,
    "servant_room": 0,
    "store_room": 0,
    "pool": 0,
    "gym": 0,
    "lift": 1,
    "parking": 1,
    "vastu_compliant": 0,
}

df = pd.DataFrame([test_input])

# Column order as per api.py
PIPELINE_INPUT_COLUMNS = [
    "area", "bedrooms", "bathrooms", "balcony", "floor",
    "prop_type", "furnished", "facing", "city", "sector",
    "pooja_room", "servant_room", "store_room", "pool", "gym",
    "lift", "parking", "vastu_compliant"
]
df = df[PIPELINE_INPUT_COLUMNS]

print("\n--- Raw Input ---")
print(df)

# Run through pipeline steps manually
X = df.copy()
for name, step in pipeline.named_steps.items():
    if name == "model":
        print("\n--- Model Step reached ---")
        print(f"Model type: {type(step)}")
        break
    X = step.transform(X)
    print(f"\n--- After {name} ---")
    if isinstance(X, pd.DataFrame):
        print(X.head())
    else:
        print(X[0])

# Final prediction
pred_log = pipeline.predict(df)
print(f"\n--- Final Result ---")
print(f"Log Prediction: {pred_log[0]}")
price_sqft = np.expm1(pred_log[0])
print(f"Price per Sqft: {price_sqft}")
print(f"Total: {price_sqft * 1200}")
