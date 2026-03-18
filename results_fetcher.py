# --------------------------------------------------
# 🔥 AUTO RESULTS FETCHER (NBA STATS SAFE MODE)
# --------------------------------------------------

import requests
from datetime import datetime

# --------------------------------------------------
# HEADERS (REQUIRED)
# --------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

# --------------------------------------------------
# FETCH TODAY'S GAMES
# --------------------------------------------------

def get_today_games():

    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

    try:
        res = requests.get(url, timeout=5)
        data = res.json()

        today = datetime.utcnow().strftime("%Y-%m-%d")

        for day in data["leagueSchedule"]["gameDates"]:
            if day["gameDate"] == today:
                return day.get("games", [])

        return []

    except Exception as e:
        print("❌ SCHEDULE FETCH ERROR:", e)
        return []


# --------------------------------------------------
# FETCH BOX SCORE
# --------------------------------------------------

def get_boxscore(game_id):

    url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"

    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        return res.json()
    except:
        return None


# --------------------------------------------------
# BUILD PLAYER RESULTS
# --------------------------------------------------

def build_results():

    games = get_today_games()

    results = {}

    for game in games:

        game_id = game.get("gameId")

        if not game_id:
            continue

        box = get_boxscore(game_id)

        if not box:
            continue

        try:
            players = box["game"]["homeTeam"]["players"] + box["game"]["awayTeam"]["players"]

            for p in players:

                name = f"{p['firstName']} {p['familyName']}"

                stats = p.get("statistics", {})

                results[name] = {
                    "points": stats.get("points", 0),
                    "rebounds": stats.get("reboundsTotal", 0),
                    "assists": stats.get("assists", 0)
                }

        except:
            continue

    return results