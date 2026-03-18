# --------------------------------------------------
# 🔥 REAL PLAYER DATA ENGINE (NBA STATS API)
# --------------------------------------------------

import requests

# --------------------------------------------------
# HEADERS (REQUIRED OR NBA BLOCKS YOU)
# --------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com"
}

# --------------------------------------------------
# CACHE (CRITICAL FOR SPEED + NO RATE LIMIT)
# --------------------------------------------------

PLAYER_ID_CACHE = {}
GAMELOG_CACHE = {}

# --------------------------------------------------
# GET PLAYER ID (FROM COMMONALLPLAYERS)
# --------------------------------------------------

def get_player_id(player_name):

    if player_name in PLAYER_ID_CACHE:
        return PLAYER_ID_CACHE[player_name]

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

            if player_name.lower() in name.lower():
                PLAYER_ID_CACHE[player_name] = p[0]  # PLAYER_ID
                return p[0]

        return None

    except Exception as e:
        print(f"❌ PLAYER ID ERROR: {player_name}", e)
        return None

# --------------------------------------------------
# GET LAST 5 GAMES
# --------------------------------------------------

def get_player_gamelog(player_name):

    if player_name in GAMELOG_CACHE:
        return GAMELOG_CACHE[player_name]

    player_id = get_player_id(player_name)

    if not player_id:
        return []

    try:
        url = "https://stats.nba.com/stats/playergamelog"

        params = {
            "PlayerID": player_id,
            "Season": "2024-25",
            "SeasonType": "Regular Season"
        }

        res = requests.get(url, headers=HEADERS, params=params, timeout=5)
        data = res.json()

        rows = data["resultSets"][0]["rowSet"]

        games = []

        for r in rows[:5]:  # last 5 games
            games.append({
                "minutes": float(r[6]),   # MIN
                "points": float(r[24]),  # PTS
                "fga": float(r[9])       # FGA
            })

        GAMELOG_CACHE[player_name] = games
        return games

    except Exception as e:
        print(f"❌ GAMELOG ERROR: {player_name}", e)
        return []

# --------------------------------------------------
# 📊 REAL PROJECTIONS
# --------------------------------------------------

def project_minutes_real(player):

    games = get_player_gamelog(player)

    if not games:
        return 30  # fallback

    mins = [g["minutes"] for g in games]

    return round(sum(mins) / len(mins), 2)


def project_usage_real(player):

    games = get_player_gamelog(player)

    if not games:
        return 0.25

    fga = [g["fga"] for g in games]

    # normalize usage
    usage = (sum(fga) / len(fga)) / 25

    return round(usage, 3)


def project_points_real(player):

    games = get_player_gamelog(player)

    if not games:
        return 25

    points = [g["points"] for g in games]

    return round(sum(points) / len(points), 2)

# --------------------------------------------------
# 🧠 HYBRID MODEL (BEST VERSION)
# --------------------------------------------------

def project_points(player):

    minutes = project_minutes_real(player)
    usage = project_usage_real(player)

    # core model
    model = minutes * usage * 1.3

    # blend with actual recent scoring
    real_pts = project_points_real(player)

    final = (model * 0.6) + (real_pts * 0.4)

    return round(final, 2)