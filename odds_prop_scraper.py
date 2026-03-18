# --------------------------------------------------
# 🔥 ODDS PROP SCRAPER (STABLE + NO 422 ERRORS)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

BASE_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ✅ ONLY SAFE MARKET (expand later if confirmed working)
MARKETS = ["player_points"]


# --------------------------------------------------
# FETCH MARKET (SAFE)
# --------------------------------------------------

def fetch_market(market):

    if not API_KEY:
        print("❌ ODDS_API_KEY missing")
        return []

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": market,
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=6)

        if res.status_code == 422:
            print(f"⚠️ Market not supported: {market}")
            return []

        if res.status_code != 200:
            print(f"❌ Odds API error ({market}): {res.status_code}")
            return []

        return res.json()

    except Exception as e:
        print(f"❌ FETCH ERROR ({market}):", e)
        return []


# --------------------------------------------------
# PARSE PROPS
# --------------------------------------------------

def parse_props(data):

    props = []

    for game in data:

        for book in game.get("bookmakers", []):

            for market in book.get("markets", []):

                if market.get("key") != "player_points":
                    continue

                for outcome in market.get("outcomes", []):

                    player = outcome.get("description")
                    line = outcome.get("point")

                    if not player or line is None:
                        continue

                    props.append({
                        "player": player.strip(),
                        "stat": "points",
                        "line": float(line)
                    })

    return props


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------

def get_odds_props():

    all_props = []

    for market in MARKETS:

        data = fetch_market(market)

        if not data:
            continue

        parsed = parse_props(data)
        all_props.extend(parsed)

    print(f"📊 Odds props loaded: {len(all_props)}")

    return all_props
