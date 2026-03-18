# --------------------------------------------------
# 🔥 ELITE PLAYER DATA ENGINE (STABLE + HYBRID + NO TIMEOUTS)
# --------------------------------------------------

import requests
import time

# --------------------------------------------------
# 🔒 MASTER SWITCH (CRITICAL)
# --------------------------------------------------
# Disable external NBA API (blocked on Railway)
DISABLE_EXTERNAL_STATS = True

# --------------------------------------------------
# HEADERS (ONLY USED IF ENABLED)
# --------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

# --------------------------------------------------
# CACHE SYSTEM (FUTURE-PROOF)
# --------------------------------------------------

PLAYER_ID_CACHE = {}
GAMELOG_CACHE = {}
CACHE_EXPIRY = 300  # seconds

# --------------------------------------------------
# 🔥 DEFAULT FALLBACK STATS (VERY IMPORTANT)
# --------------------------------------------------

DEFAULT_STATS = {
    "LeBron James": {"minutes": 35, "points": 25, "usage": 0.30},
    "Stephen Curry": {"minutes": 34, "points": 27, "usage": 0.32},
    "Luka Doncic": {"minutes": 36, "points": 30, "usage": 0.36},
    "Nikola Jokic": {"minutes": 34, "points": 26, "usage": 0.31}
}

# --------------------------------------------------
# SAFE REQUEST (ONLY USED IF ENABLED)
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
# PLAYER ID (DISABLED SAFE MODE)
# --------------------------------------------------

def get_player_id(player_name):

    if DISABLE_EXTERNAL_STATS:
        return None

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
        return None

    try:
        for p in data["resultSets"][0]["rowSet"]:
            if player_name.lower() in p[2].lower():
                PLAYER_ID_CACHE[player_name] = p[0]
                return p[0]
    except:
        pass

    return None

# --------------------------------------------------
# GAMELOG (DISABLED SAFE MODE)
# --------------------------------------------------

def get_player_gamelog(player_name):

    if DISABLE_EXTERNAL_STATS:
        return []

    if player_name in GAMELOG_CACHE:
        data, ts = GAMELOG_CACHE[player_name]

        if time.time() - ts < CACHE_EXPIRY:
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
# 📊 REAL PROJECTIONS (WITH FALLBACK)
# --------------------------------------------------

def project_minutes_real(player):

    games = get_player_gamelog(player)

    if not games:
        val = DEFAULT_STATS.get(player, {}).get("minutes", 32)
        print(f"⚠️ Using fallback minutes for {player}: {val}")
        return val

    return round(sum(g["minutes"] for g in games) / len(games), 2)


def project_usage_real(player):

    games = get_player_gamelog(player)

    if not games:
        val = DEFAULT_STATS.get(player, {}).get("usage", 0.25)
        print(f"⚠️ Using fallback usage for {player}: {val}")
        return val

    usage = (sum(g["fga"] for g in games) / len(games)) / 25

    return round(usage, 3)


def project_points_real(player):

    games = get_player_gamelog(player)

    if not games:
        val = DEFAULT_STATS.get(player, {}).get("points", 24)
        print(f"⚠️ Using fallback points for {player}: {val}")
        return val

    return round(sum(g["points"] for g in games) / len(games), 2)

# --------------------------------------------------
# 🔥 FINAL HYBRID MODEL (UPGRADED)
# --------------------------------------------------

def project_points(player):

    minutes = project_minutes_real(player)
    usage = project_usage_real(player)

    # base model
    model_projection = minutes * usage * 1.3

    real_projection = project_points_real(player)

    # 🔥 balanced blend
    final = (model_projection * 0.5) + (real_projection * 0.5)

    return round(final, 2)