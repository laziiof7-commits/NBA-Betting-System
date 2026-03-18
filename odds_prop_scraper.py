# --------------------------------------------------
# 🔥 ODDS API PROP SCRAPER (BEST LINE + SAFE)
# --------------------------------------------------

import requests
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

API_KEY = os.getenv("ODDS_API_KEY")

URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# --------------------------------------------------
# MARKET MAP
# --------------------------------------------------

def map_market(key):

    return {
        "player_points": "points",
        "player_rebounds": "rebounds",
        "player_assists": "assists"
    }.get(key)

# --------------------------------------------------
# BEST LINE LOGIC
# --------------------------------------------------

def choose_best(existing, new_line):

    if existing is None:
        return new_line

    # 🔥 lower line is better for OVER betting
    return min(existing, new_line)

# --------------------------------------------------
# MAIN FETCH
# --------------------------------------------------

def get_odds_props():

    if not API_KEY:
        print("❌ ODDS_API_KEY missing")
        return []

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "player_points,player_rebounds,player_assists",
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(URL, params=params, headers=HEADERS, timeout=6)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        data = res.json()

        best_lines = {}

        for game in data:

            for book in game.get("bookmakers", []):

                for market in book.get("markets", []):

                    stat = map_market(market.get("key"))

                    if not stat:
                        continue

                    for o in market.get("outcomes", []):

                        player = o.get("description")
                        line = o.get("point")

                        if not player or line is None:
                            continue

                        player = player.strip()

                        # init player
                        if player not in best_lines:
                            best_lines[player] = {}

                        existing = best_lines[player].get(stat)

                        best_lines[player][stat] = choose_best(existing, line)

        # --------------------------------------------------
        # CLEAN OUTPUT
        # --------------------------------------------------

        props = []

        for player, stats in best_lines.items():

            for stat, line in stats.items():

                props.append({
                    "player": player,
                    "stat": stat,
                    "line": line
                })

        print(f"✅ Best lines loaded: {len(props)}")

        return props

    except Exception as e:
        print("❌ Odds fetch failed:", e)
        return []
        return []
