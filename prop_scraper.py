# --------------------------------------------------
# 🔥 ELITE PROP SCRAPER (BEST LINE + CLV READY)
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
# 📥 FETCH RAW DATA
# --------------------------------------------------

def fetch_odds():

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
            print(f"❌ API ERROR: {res.status_code}")
            return []

        return res.json()

    except Exception as e:
        print("❌ FETCH ERROR:", e)
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
# 🎯 BEST LINE LOGIC (SMART)
# --------------------------------------------------

def choose_best(existing, new):

    if existing is None:
        return new

    # prefer better price OR better line
    if new["line"] < existing["line"]:
        return new

    if new["line"] == existing["line"]:
        if new["price"] > existing["price"]:
            return new

    return existing


# --------------------------------------------------
# 🔥 MAIN SCRAPER
# --------------------------------------------------

def get_player_props():

    raw = fetch_odds()

    props = {}

    for game in raw:

        for book in game.get("bookmakers", []):

            book_name = book.get("title", "Unknown")

            for market in book.get("markets", []):

                stat = map_market(market.get("key"))

                if not stat:
                    continue

                for o in market.get("outcomes", []):

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
                        "implied": implied_prob(price)
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
                "implied_prob": data["implied"]
            })

    return cleaned