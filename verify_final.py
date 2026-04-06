import urllib.request
import json

def get_valuation(sector):
    url = "http://localhost:8000/predict"
    payload = {
        "city": "Noida",
        "sector": sector,
        "area": 1800,
        "bedrooms": 3,
        "listing_type": "buy"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return json.loads(res_body)['estimated_market_value']
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("--- INSTITUTIONAL API VERIFICATION (Sector 150 vs 62) ---")
    v150 = get_valuation("Sector 150")
    v62 = get_valuation("Sector 62")
    
    # If the fix works, Sector 150 (mapped to 137) will be different from Sector 62
    print(f"Sector 150 Valuation:  ₹{v150:,.0f}" if isinstance(v150, (int, float)) else f"FAILED: {v150}")
    print(f"Sector 62 Valuation:   ₹{v62:,.0f}" if isinstance(v62, (int, float)) else f"FAILED: {v62}")
    
    if isinstance(v150, (int, float)) and isinstance(v62, (int, float)):
        if v150 != v62:
            print("\nVERIFICATION: SUCCESS. Different sectors now produce unique valuations.")
        else:
            print("\nVERIFICATION: FAILED. Metrics are still identical across sectors.")
