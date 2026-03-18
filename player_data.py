# --------------------------------------------------
# 🔥 ELITE PLAYER DATA ENGINE (FAST + SAFE + CACHED)
# --------------------------------------------------

import requests
import time

# --------------------------------------------------
# HEADERS (CRITICAL)
# --------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

# --------------------------------------------------
# CACHE (CRITICAL FOR PERFORMANCE)
# --------------------------------------------------

PLAYER_ID_CACHE = {}
GAMELOG_CACHE = {}
CACHE_EXPIRY = 300  # seconds

# --------------------------------------------------
# DEFAULT FALLBACK STATS (VERY IMPORTANT)
# --------------------------------------------------

DEFAULT_STATS = {
    "LeBron James": {"minutes": 35, "points": 25, "usage": 0.30},
    "Stephen Curry": {"minutes": 34, "points": 27, "usage": 0.32},
    "Luka Doncic": {"minutes": 36, "points": 30, "usage": 0.36},
    "Nikola Jokic": {"minutes": 34, "points": 26, "usage": 0.31}
}

# --------------------------------------------------
# SAFE REQUEST
# --------------------------------------------------

def safe_get(url, params=None):

    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=3)

        if res.status_code != 200:
            return None

        return res.json()

    except:
        return None

# --------------------------------------------------
# PLAYER ID
# --------------------------------------------------

def get_player_id(player_name):

    if player_name in PLAYER_ID_CACHE:
        return PLAYER_ID_CACHE[player_name]

    url = "https://stats.nba.com/stats/commonallplayers"

    params = {
        "LeagueID": "00",
        "Season": "2024-25",
        "IsOnlyCurrentSeason": "1"
    }

    data = safe_get(url, params)

    if not data:
        print(f"⚠️ Player ID fallback: {player_name}")
        return None

    try:
        players = data["resultSets"][0]["rowSet"]

        for p in players:
            name = p[2]

            if player_name.lower() in name.lower():
                PLAYER_ID_CACHE[player_name] = p[0]
                return p[0]

    except:
        pass

    return None

# --------------------------------------------------
# GAMELOG (CACHED + SAFE)
# --------------------------------------------------

def get_player_gamelog(player_name):

    # 🔥 CACHE CHECK
    if player_name in GAMELOG_CACHE:

        data, timestamp = GAMELOG_CACHE[player_name]

        if time.time() - timestamp < CACHE_EXPIRY:
            return data

    player_id = get_player_id(player_name)

    if not player_id:
        return []

    url = "https://stats.nba.com/stats/playergamelog"

    params = {
        "PlayerID": player_id,
        "Season": "2024-25",
        "SeasonType": "Regular Season"
    }

    data = safe_get(url, params)

    if not data:
        print(f"⚠️ GAMELOG fallback: {player_name}")
        return []

    try:
        rows = data["resultSets"][0]["rowSet"]

        games = []

        for r in rows[:5]:
            games.append({
                "minutes": float(r[6]),
                "points": float(r[24]),
                "fga": float(r[9])
            })

        GAMELOG_CACHE[player_name] = (games, time.time())

        return games

    except:
        return []

# --------------------------------------------------
# REAL PROJECTIONS (SAFE)
# --------------------------------------------------

def project_minutes_real(player):

    games = get_player_gamelog(player)

    if not games:
        return DEFAULT_STATS.get(player, {}).get("minutes", 32)

    return round(sum(g["minutes"] for g in games) / len(games), 2)


def project_usage_real(player):

    games = get_player_gamelog(player)

    if not games:
        return DEFAULT_STATS.get(player, {}).get("usage", 0.25)

    usage = (sum(g["fga"] for g in games) / len(games)) / 25

    return round(usage, 3)


def project_points_real(player):

    games = get_player_gamelog(player)

    if not games:
        return DEFAULT_STATS.get(player, {}).get("points", 24)

    return round(sum(g["points"] for g in games) / len(games), 2)

# --------------------------------------------------
# 🔥 HYBRID MODEL (UPGRADED)
# --------------------------------------------------

def project_points(player):

    minutes = project_minutes_real(player)
    usage = project_usage_real(player)

    # base model
    model = minutes * usage * 1.3

    real_pts = project_points_real(player)

    # 🔥 smarter weighting
    final = (model * 0.5) + (real_pts * 0.5)

    return round(final, 2)