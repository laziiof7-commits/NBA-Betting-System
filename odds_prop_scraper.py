# --------------------------------------------------
# 🔥 ODDS API INTEGRATION (STABLE MODE)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY") or "cb851ffe64d928cce8294684d8f8b74c"

SPORT = "basketball_nba"
REGION = "us"
MARKETS = "spreads,totals"

URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

# --------------------------------------------------
# FETCH ODDS
# --------------------------------------------------

def fetch_odds():

    try:
        params = {
            "apiKey": API_KEY,
            "regions": REGION,
            "markets": MARKETS,
            "oddsFormat": "american"
        }

        res = requests.get(URL, params=params, timeout=10)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        return res.json()

    except Exception as e:
        print("❌ ODDS API ERROR:", e)
        return []

# --------------------------------------------------
# CONVERT TO SYSTEM FORMAT
# --------------------------------------------------

def parse_games(data):

    props = []

    for game in data:

        home = game.get("home_team")
        away = game.get("away_team")

        if not home or not away:
            continue

        game_name = f"{away} @ {home}"

        bookmakers = game.get("bookmakers", [])

        for book in bookmakers:

            for market in book.get("markets", []):

                key = market.get("key")

                for outcome in market.get("outcomes", []):

                    try:
                        if key == "totals":

                            props.append({
                                "player": game_name,
                                "stat": "total",
                                "line": float(outcome["point"]),
                                "book": book.get("title")
                            })

                        elif key == "spreads":

                            props.append({
                                "player": game_name,
                                "stat": "spread",
                                "line": float(outcome["point"]),
                                "book": book.get("title")
                            })

                    except:
                        continue

    print(f"📊 Odds API games: {len(props)}")

    return props

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def get_odds_props():

    data = fetch_odds()

    if not data:
        return []

    return parse_games(data)
