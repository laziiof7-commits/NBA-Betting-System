# --------------------------------------------------
# 🔥 PRIZEPICKS SCRAPER (FIXED + SAFE + PRODUCTION)
# --------------------------------------------------

import requests

URL = "https://api.prizepicks.com/projections?league_id=7"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# --------------------------------------------------
# FETCH DATA (SAFE)
# --------------------------------------------------

def fetch_data():

    try:
        res = requests.get(URL, headers=HEADERS, timeout=8)

        if res.status_code != 200:
            print(f"❌ PrizePicks status: {res.status_code}")
            return None

        if not res.text:
            print("❌ Empty response from PrizePicks")
            return None

        return res.json()

    except Exception as e:
        print("❌ PRIZEPICKS FETCH ERROR:", e)
        return None


# --------------------------------------------------
# MAIN SCRAPER
# --------------------------------------------------

def get_prizepicks_props():

    data = fetch_data()

    if not data:
        print("⚠️ No PrizePicks data")
        return []

    try:

        players = {
            p["id"]: p for p in data.get("included", [])
        }

        props = []

        for item in data.get("data", []):

            attr = item.get("attributes", {})

            player_id = (
                item.get("relationships", {})
                .get("new_player", {})
                .get("data", {})
                .get("id")
            )

            if not player_id:
                continue

            player_info = players.get(player_id, {}).get("attributes", {})

            player_name = player_info.get("name")
            stat_type = attr.get("stat_type")
            line = attr.get("line_score")

            if not player_name or line is None:
                continue

            props.append({
                "player": player_name,
                "stat": stat_type.lower(),
                "line": line
            })

        print(f"✅ PrizePicks props: {len(props)}")

        return props

    except Exception as e:
        print("❌ PARSE ERROR:", e)
        return []