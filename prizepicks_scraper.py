# --------------------------------------------------
# 🔥 PRIZEPICKS SCRAPER (ANTI-BLOCK + STABLE)
# --------------------------------------------------

import requests
import time
import random

URL = "https://api.prizepicks.com/projections?league_id=7"

# 🔥 HEADERS (CRITICAL — prevents 403)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://app.prizepicks.com/",
    "Origin": "https://app.prizepicks.com",
    "Connection": "keep-alive"
}

# rate limit protection
LAST_CALL = 0


def rate_limit():
    global LAST_CALL

    now = time.time()

    if now - LAST_CALL < 2:
        time.sleep(2 + random.random())

    LAST_CALL = time.time()


# --------------------------------------------------
# 🔥 MAIN SCRAPER
# --------------------------------------------------

def get_prizepicks_props():

    rate_limit()

    try:
        res = requests.get(URL, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            print(f"❌ PrizePicks error: {res.status_code}")
            return []

        data = res.json()

        players = {
            p["id"]: p["attributes"]
            for p in data.get("included", [])
            if p.get("type") == "new_player"
        }

        props = []

        for item in data.get("data", []):

            attr = item.get("attributes", {})
            rel = item.get("relationships", {})

            player_id = rel.get("new_player", {}).get("data", {}).get("id")

            if not player_id:
                continue

            player_info = players.get(player_id)

            if not player_info:
                continue

            player_name = player_info.get("name")
            stat_type = attr.get("stat_type")
            line = attr.get("line_score")

            if not player_name or line is None:
                continue

            stat_map = {
                "Points": "points",
                "Rebounds": "rebounds",
                "Assists": "assists",
                "Pts+Rebs+Asts": "pra"
            }

            stat = stat_map.get(stat_type)

            if not stat:
                continue

            props.append({
                "player": player_name.strip(),
                "stat": stat,
                "line": float(line)
            })

        print(f"✅ PrizePicks props pulled: {len(props)}")

        return props

    except Exception as e:
        print("❌ PRIZEPICKS ERROR:", e)
        return []
