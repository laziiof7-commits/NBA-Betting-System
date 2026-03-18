import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

def get_odds_props():

    if not API_KEY:
        print("❌ Missing ODDS_API_KEY")
        return []

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "totals"  # ✅ ONLY VALID MARKET
    }

    try:
        res = requests.get(url, params=params, timeout=10)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        data = res.json()

        print(f"✅ Odds API working (games: {len(data)})")

        # ⚠️ This API does NOT give player props → return empty
        return []

    except Exception as e:
        print("❌ SCRAPER ERROR:", e)
        return []
