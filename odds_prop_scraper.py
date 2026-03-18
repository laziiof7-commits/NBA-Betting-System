# --------------------------------------------------
# 🔥 ODDS API PROP SCRAPER (CLEAN + NO 422)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

BASE_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

MARKETS = [
    "player_points",
    "player_rebounds",
    "player_assists"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# --------------------------------------------------
# FETCH SINGLE MARKET (CRITICAL FIX)
# --------------------------------------------------

def fetch_market(market):

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": market,
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=6)

        if res.status_code != 200:
            print(f"❌ Odds API error ({market}): {res.status_code}")
            return []

        return res.json()

    except Exception as e:
        print(f"❌ FETCH ERROR ({market}):", e)
        return []

# --------------------------------------------------
# IMPLIED PROB
# --------------------------------------------------

def implied_prob(price):
    if not price:
        return None
    return round(1 / price, 3)

# --------------------------------------------------
# BEST LINE SELECTION
# --------------------------------------------------

def choose_best(existing, new):

    if existing is None:
        return new

    # better line
    if new["line"] < existing["line"]:
        return new

    # same line → better odds
    if new["line"] == existing["line"]:
        if new["price"] and existing["price"]:
            if new["price"] > existing["price"]:
                return new

    return existing

# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def get_odds_props():

    if not API_KEY:
        print("❌ ODDS_API_KEY missing")
        return []

    props = {}

    for market in MARKETS:

        raw = fetch_market(market)

        for game in raw:

            for book in game.get("bookmakers", []):

                book_name = book.get("title", "Unknown")

                for m in book.get("markets", []):

                    stat_map = {
                        "player_points": "points",
                        "player_rebounds": "rebounds",
                        "player_assists": "assists"
                    }

                    stat = stat_map.get(m.get("key"))

                    if not stat:
                        continue

                    for o in m.get("outcomes", []):

                        player = o.get("description")
                        line = o.get("point")
                        price = o.get("price")

                        if not player or line is None:
                            continue

                        entry = {
                            "line": line,
                            "price": price,
                            "book": book_name,
                            "implied_prob": implied_prob(price)
                        }

                        if player not in props:
                            props[player] = {}

                        existing = props[player].get(stat)

                        props[player][stat] = choose_best(existing, entry)

    # ---------------- CLEAN FORMAT ----------------

    cleaned = []

    for player, stats in props.items():
        for stat, data in stats.items():

            cleaned.append({
                "player": player,
                "stat": stat,
                "line": data["line"],
                "price": data["price"],
                "book": data["book"],
                "implied_prob": data["implied_prob"]
            })

    print(f"📊 Odds props loaded: {len(cleaned)}")

    return cleaned
