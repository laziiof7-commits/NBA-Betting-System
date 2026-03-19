# --------------------------------------------------
# 🏀 TEAM DATA (LIVE UPDATE)
# --------------------------------------------------

import requests
import time

TEAM_STATS = {}
LAST_UPDATE = 0

UPDATE_INTERVAL = 60 * 60 * 6  # every 6 hours

def fetch_team_stats():

    global TEAM_STATS, LAST_UPDATE

    try:
        url = "https://api.balldontlie.io/v1/teams"
        res = requests.get(url, timeout=10)
        data = res.json()["data"]

        new_stats = {}

        for t in data:
            name = t["full_name"]

            # 🔥 fallback simple stats (can expand later)
            new_stats[name] = {
                "pace": 100,
                "off": 112,
                "def": 112
            }

        TEAM_STATS = new_stats
        LAST_UPDATE = time.time()

        print("✅ TEAM DATA UPDATED")

    except Exception as e:
        print("❌ TEAM DATA ERROR:", e)

def get_team_stats():

    if time.time() - LAST_UPDATE > UPDATE_INTERVAL:
        fetch_team_stats()

    return TEAM_STATS