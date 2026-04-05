import requests
import json

url = "http://127.0.0.1:8000/predict"
payload = {
    "area": 1500,
    "bedrooms": 3,
    "prop_type": "Apartment",
    "furnishing_status": "Semi-Furnished",
    "legal_status": "Freehold",
    "city": "Gurgaon",
    "sector": "Sector 54",
    "property_name": "DLF The Aralias",
    "listing_type": "buy",
    "amenities": {
        "has_pool": True,
        "has_gym": True,
        "has_lift": True,
        "has_power_backup": True,
        "is_gated_community": True,
        "has_clubhouse": True,
        "has_maintenance": True,
        "has_wifi": True,
        "is_high_ceiling": True
    },
    "location_score": {
        "is_near_metro": True,
        "is_corner_property": True,
        "is_park_facing": True,
        "is_vastu_compliant": True
    },
    "features": {
        "is_luxury": True,
        "is_servant_room": True,
        "is_study_room": True,
        "is_store_room": True,
        "is_pooja_room": True,
        "is_new_construction": True
    },
    "is_rera_registered": True,
    "no_brokerage": True,
    "bachelors_allowed": False,
    "is_standalone": False,
    "is_owner_listing": True,
    "orientation": "NE",
    "property_age": 2
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        # print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")
