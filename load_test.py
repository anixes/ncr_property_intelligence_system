import requests
import time
import json
import statistics

API_URL = "http://localhost:8000/predict"

# 🏛️ Institutional Property Profile (High-Complexity)
input_data = {
    "listing_type": "buy",
    "city": "Gurgaon",
    "sector": "Sector 62",
    "prop_type": "Apartment",
    "area": 2500,
    "bedrooms": 4,
    "bathrooms": 3,
    "furnishing_status": "Semi-Furnished",
    "legal_status": "Freehold",
    "amenities": {
        "has_pool": True,
        "has_gym": True,
        "has_lift": True,
        "has_power_backup": True,
        "is_gated_community": True
    },
    "location_score": {
        "is_near_metro": True,
        "is_corner_property": False,
        "is_park_facing": True,
        "is_vastu_compliant": True
    },
    "features": {
        "is_luxury": True,
        "is_servant_room": True,
        "is_study_room": False,
        "is_store_room": True,
        "is_pooja_room": True
    }
}

def run_stress_test(count=50):
    print(f"🚀 Initializing High-Velocity Stress Test: {count} Tensors...")
    latencies = []
    
    for i in range(count):
        start = time.perf_counter()
        try:
            resp = requests.post(API_URL, json=input_data, timeout=5)
            resp.raise_for_status()
            latencies.append(time.perf_counter() - start)
            if i % 10 == 0:
                print(f"   [Batch {i}] Inference Stable...")
        except Exception as e:
            print(f"   [Batch {i}] FAILED: {e}")
    
    if not latencies:
        return None

    report = {
        "total_requests": count,
        "avg_latency_ms": round(statistics.mean(latencies) * 1000, 2),
        "min_latency_ms": round(min(latencies) * 1000, 2),
        "max_latency_ms": round(max(latencies) * 1000, 2),
        "throughput_rps": round(1 / statistics.mean(latencies), 2),
        "status": "INSTITUTIONAL GRADE" if statistics.mean(latencies) < 0.15 else "DEGRADED"
    }
    return report

if __name__ == "__main__":
    results = run_stress_test(50)
    if results:
        print("\n🏛️ --- PERFORMANCE AUDIT REPORT ---")
        print(json.dumps(results, indent=4))
    else:
        print("\n❌ Audit Failed: API Unreachable or Model Error.")
