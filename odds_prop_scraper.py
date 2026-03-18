# --------------------------------------------------
# 🔥 ODDS API PROP SCRAPER (SAFE VERSION)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"


def get_odds_props():

    if not API_KEY:
        print("❌ No ODDS_API_KEY")
        return []

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_points",
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(URL, params=params, timeout=6)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        data = res.json()

        props = []

        for game in data:

            for book in game.get("bookmakers", []):

                for market in book.get("markets", []):

                    if market.get("key") != "player_points":
                        continue

                    for o in market.get("outcomes", []):

                        player = o.get("description")
                        line = o.get("point")

                        if not player or line is None:
                            continue

                        props.append({
                            "player": player.strip(),
                            "stat": "points",
                            "line": line
                        })

        print(f"✅ Loaded real props: {len(props)}")

        return props

    except Exception as e:
        print("❌ Odds fetch failed:", e)
        return []