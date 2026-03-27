import requests

def test_api():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    # Let's try some typical housing.com endpoints!
    url = "https://housing.com/api/v0/search/suggest/popular?source=web"
    try:
        r = requests.get(url, headers=headers)
        print(r.text[:500])
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    test_api()
