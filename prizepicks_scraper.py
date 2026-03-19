# --------------------------------------------------
# 🔥 PRIZEPICKS SCRAPER (FINAL STEALTH VERSION)
# --------------------------------------------------

import requests
import time
import random

URL = "https://api.prizepicks.com/projections?league_id=7"

# ---------------- CONFIG ----------------

MAX_RETRIES = 3
LAST_CALL = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

# ---------------- SESSION ----------------

session = requests.Session()

def build_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://app.prizepicks.com/",
        "Origin": "https://app.prizepicks.com",
        "Connection": "keep-alive"
    }

# ---------------- RATE LIMIT ----------------

def rate_limit():
    global LAST_CALL

    now = time.time()

    if now - LAST_CALL < 2:
        sleep_time = 2 + random.uniform(0.5, 1.5)
        print(f"⏳ Rate limit sleep: {round(sleep_time,2)}s")
        time.sleep(sleep_time)

    LAST_CALL = time.time()

# --------------------------------------------------
# 🔥 MAIN SCRAPER
# --------------------------------------------------

def get_prizepicks_props():

    for attempt in range(MAX_RETRIES):

        try:
            rate_limit()

            headers = build_headers()

            res = session.get(URL, headers=headers, timeout=10)

            if res.status_code == 403:
                print(f"❌ BLOCKED (attempt {attempt+1})")
                time.sleep(3)
                continue

            if res.status_code == 429:
                print("⏳ RATE LIMITED — retrying")
                time.sleep(5)
                continue

            if res.status_code != 200:
                print(f"❌ PrizePicks error: {res.status_code}")
                return []

            data = res.json()

            # ---------------- PLAYER MAP ----------------
            players = {
                p["id"]: p["attributes"]
                for p in data.get("included", [])
                if p.get("type") == "new_player"
            }

            props = []

            # ---------------- PARSE ----------------
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
                    "line": float(line),
                    "book": "PrizePicks"  # 🔥 CRITICAL ADD
                })

            print(f"✅ PrizePicks props pulled: {len(props)}")

            return props

        except Exception as e:
            print("❌ PRIZEPICKS ERROR:", e)

    print("🚨 PrizePicks failed after retries")
    return []
