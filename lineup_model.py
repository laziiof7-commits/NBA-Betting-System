# --------------------------------------------------
# 🔥 ELITE LINEUP MODEL (STARTERS + MINUTES BOOST)
# --------------------------------------------------

import requests
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CACHE = {}
LAST_FETCH = 0
CACHE_TTL = 120  # 2 min


# --------------------------------------------------
# FETCH LIVE LINEUPS
# --------------------------------------------------

def fetch_lineups():

    global CACHE, LAST_FETCH

    now = time.time()

    if now - LAST_FETCH < CACHE_TTL:
        return CACHE

    try:
        res = requests.get(URL, headers=HEADERS, timeout=5)
        data = res.json()

        lineups = {}

        for game in data.get("scoreboard", {}).get("games", []):

            for side in ["homeTeam", "awayTeam"]:

                team = game[side]["teamName"]

                starters = []

                for p in game[side].get("players", []):

                    if p.get("starter"):
                        name = f"{p['firstName']} {p['familyName']}"
                        starters.append(name)

                lineups[team] = starters

        CACHE = lineups
        LAST_FETCH = now

        return lineups

    except Exception as e:
        print("❌ LINEUP FETCH ERROR:", e)
        return {}


# --------------------------------------------------
# CHECK IF STARTER
# --------------------------------------------------

def is_starter(player, team):

    lineups = fetch_lineups()

    if not team or team not in lineups:
        return None  # unknown

    return player in lineups[team]


# --------------------------------------------------
# MINUTES BOOST (CORE LOGIC)
# --------------------------------------------------

def minutes_boost(player, team=None):

    try:
        starter = is_starter(player, team)

        # unknown → no adjustment
        if starter is None:
            return 0

        # 🔥 STARTER BOOST
        if starter:
            return 3.5  # +3.5 projected points impact

        # 🔻 BENCH PENALTY
        return -2.5

    except:
        return 0


# --------------------------------------------------
# USAGE BOOST FROM LINEUP CHANGES
# --------------------------------------------------

def lineup_usage_boost(player, team=None):

    lineups = fetch_lineups()

    if not team or team not in lineups:
        return 0

    starters = lineups[team]

    # if star missing from lineup → boost others
    missing_stars = [
        "LeBron James",
        "Stephen Curry",
        "Luka Doncic",
        "Nikola Jokic"
    ]

    boost = 0

    for star in missing_stars:

        if star not in starters:
            boost += 1.5

    return boost


# --------------------------------------------------
# FINAL LINEUP ADJUSTMENT
# --------------------------------------------------

def lineup_adjustment(team=None, opponent=None):

    # lightweight version for game totals
    return 0


# --------------------------------------------------
# PLAYER-LEVEL ADJUSTMENT (USED IN PROP MODEL)
# --------------------------------------------------

def player_lineup_adjustment(player, team=None):

    try:
        boost = 0

        boost += minutes_boost(player, team)
        boost += lineup_usage_boost(player, team)

        return round(boost, 2)

    except Exception as e:
        print("❌ LINEUP MODEL ERROR:", e)
        return 0
