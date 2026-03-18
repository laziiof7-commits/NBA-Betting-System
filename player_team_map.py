# --------------------------------------------------
# 🔥 PLAYER → TEAM MAP (NBA API SAFE)
# --------------------------------------------------

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

CACHE = {}


# --------------------------------------------------
# FETCH PLAYER TEAM
# --------------------------------------------------

def get_player_team(player_name):

    if player_name in CACHE:
        return CACHE[player_name]

    try:
        url = "https://stats.nba.com/stats/commonallplayers"

        params = {
            "LeagueID": "00",
            "Season": "2024-25",
            "IsOnlyCurrentSeason": "1"
        }

        res = requests.get(url, headers=HEADERS, params=params, timeout=5)
        data = res.json()

        players = data["resultSets"][0]["rowSet"]

        for p in players:

            name = p[2]  # PLAYER_NAME
            team = p[7]  # TEAM_NAME

            if player_name.lower() in name.lower():

                CACHE[player_name] = team
                return team

        return None

    except Exception as e:
        print("❌ TEAM MAP ERROR:", e)
        return None


# --------------------------------------------------
# BUILD TEAM MAP FROM SCHEDULE
# --------------------------------------------------

def build_opponent_map(schedule):

    team_map = {}

    for date, games in schedule.items():
        for g in games.values():

            home = g["home_team"]
            away = g["away_team"]

            team_map[home] = away
            team_map[away] = home

    return team_map