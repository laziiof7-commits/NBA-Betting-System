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
        "markets": "player_points,player_rebounds,player_assists",
        "oddsFormat": "american"
    }

    try:
        res = requests.get(url, params=params, timeout=10)

        if res.status_code != 200:
            print(f"❌ Odds API error: {res.status_code}")
            return []

        data = res.json()

        props = []

        for game in data:

            for book in game.get("bookmakers", []):

                for market in book.get("markets", []):

                    stat_map = {
                        "player_points": "points",
                        "player_rebounds": "rebounds",
                        "player_assists": "assists"
                    }

                    stat = stat_map.get(market["key"])

                    if not stat:
                        continue

                    for outcome in market.get("outcomes", []):

                        player = outcome.get("description")
                        line = outcome.get("point")

                        if player and line:
                            props.append({
                                "player": player,
                                "stat": stat,
                                "line": line
                            })

        print(f"✅ Pulled {len(props)} sportsbook props")

        return props

    except Exception as e:
        print("❌ SCRAPER ERROR:", e)
        return []
