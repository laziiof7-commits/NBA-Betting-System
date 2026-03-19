# --------------------------------------------------
# 📊 ODDS SCRAPER (REAL API + MULTI-BOOK)
# --------------------------------------------------

import requests
import os

API_KEY = os.getenv("ODDS_API_KEY")

SPORT = "basketball_nba"

BOOKS = ["draftkings", "fanduel"]

def get_odds_props():

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "spreads,totals",
        "oddsFormat": "american"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
    except Exception as e:
        print("❌ Odds API error:", e)
        return []

    props = []

    for game in data:

        home = game.get("home_team")
        away = game.get("away_team")

        game_name = f"{away} @ {home}"

        for book in game.get("bookmakers", []):

            if book["key"] not in BOOKS:
                continue

            for market in book.get("markets", []):

                # ---------------- SPREAD ----------------
                if market["key"] == "spreads":

                    for outcome in market["outcomes"]:

                        props.append({
                            "game": game_name,
                            "stat": "spread",
                            "team": outcome["name"],
                            "line": outcome["point"],
                            "book": book["key"]
                        })

                # ---------------- TOTAL ----------------
                if market["key"] == "totals":

                    for outcome in market["outcomes"]:

                        props.append({
                            "game": game_name,
                            "stat": "total",
                            "side": outcome["name"],
                            "line": outcome["point"],
                            "book": book["key"]
                        })

    print(f"📊 Odds API games: {len(data)}")

    return props
