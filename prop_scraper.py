# --------------------------------------------------
# 🔥 ELITE PROP SCRAPER (SAFE + SMART + NO 422 ERRORS)
# --------------------------------------------------

import requests
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

API_KEY = os.getenv("ODDS_API_KEY")

BASE_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# SAFE MARKETS (tested working)
MARKETS = [
    "player_points",
    # we will expand later safely
]

# --------------------------------------------------
# 📥 FETCH (SAFE + FALLBACK)
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

        if res.status_code != 200:
            print(f"⚠️ {market} failed ({res.status_code})")
            return []

        return res.json()

    except Exception as e:
        print(f"❌ FETCH ERROR ({market}):", e)
        return []

# --------------------------------------------------
# 🧠 MARKET MAP
# --------------------------------------------------

def map_market(key):

    return {
        "player_points": "points",
        "player_rebounds": "rebounds",
        "player_assists": "assists"
    }.get(key)

# --------------------------------------------------
# 💰 IMPLIED PROBABILITY
# --------------------------------------------------

def implied_prob(price):
    if not price:
        return None
    return round(1 / price, 3)

# --------------------------------------------------
# 🎯 BEST LINE LOGIC
# --------------------------------------------------

def choose_best(existing, new):

    if existing is None:
        return new

    # better line wins
    if new["line"] < existing["line"]:
        return new

    # same line → better price
    if new["line"] == existing["line"]:
        if new["price"] and existing["price"]:
            if new["price"] > existing["price"]:
                return new

    return existing

# --------------------------------------------------
# 🔥 MAIN SCRAPER
# --------------------------------------------------

def get_player_props():

    props = {}

    for market in MARKETS:

        raw = fetch_market(market)

        for game in raw:

            for book in game.get("bookmakers", []):

                book_name = book.get("title", "Unknown")

                for m in book.get("markets", []):

                    stat = map_market(m.get("key"))

                    if not stat:
                        continue

                    for o in m.get("outcomes", []):

                        player = o.get("description")
                        line = o.get("point")
                        price = o.get("price")

                        if not player or line is None:
                            continue

                        player = player.strip()

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

    # --------------------------------------------------
    # 🔄 CLEAN FORMAT
    # --------------------------------------------------

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

    return cleaned