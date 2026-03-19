# --------------------------------------------------
# 🔥 ODDS SCRAPER (REAL + SAFE)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

SPORT = "basketball_nba"
REGIONS = "us"
MARKETS = "totals"   # ✅ SAFE MARKET (NO 422 ERRORS)


# --------------------------------------------------
# FETCH ODDS
# --------------------------------------------------

def fetch_odds():

    if not API_KEY:
        print("❌ Missing ODDS_API_KEY")
        return []

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS
    }

    try:
        res = requests.get(url, params=params, timeout=5)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        return res.json()

    except Exception as e:
        print("❌ ODDS FETCH ERROR:", e)
        return []


# --------------------------------------------------
# PARSE INTO SYSTEM FORMAT
# --------------------------------------------------

def get_odds_props():

    data = fetch_odds()

    props = []

    for game in data:

        try:
            home = game["home_team"]
            away = game["away_team"]

            for book in game.get("bookmakers", []):
                for market in book.get("markets", []):

                    if market["key"] != "totals":
                        continue

                    for outcome in market["outcomes"]:

                        if outcome["name"] == "Over":

                            props.append({
                                "player": f"{away} vs {home}",
                                "stat": "total",
                                "line": outcome["point"]
                            })

        except:
            continue

    print(f"📊 REAL ODDS LOADED: {len(props)}")

    return props
