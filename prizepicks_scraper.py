# --------------------------------------------------
# 🔥 PRIZEPICKS SCRAPER (SAFE + NO CRASHES)
# --------------------------------------------------

import requests

URL = "https://api.prizepicks.com/projections?league_id=7"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_prizepicks_props():

    try:
        res = requests.get(URL, headers=HEADERS, timeout=8)

        # ❌ BAD STATUS
        if res.status_code != 200:
            print("❌ PrizePicks status:", res.status_code)
            return []

        # ❌ BAD JSON
        try:
            data = res.json()
        except:
            print("❌ PrizePicks returned invalid JSON")
            return []

        players = {p["id"]: p for p in data.get("included", [])}
        props = []

        for item in data.get("data", []):

            attr = item.get("attributes", {})
            player_id = item.get("relationships", {}).get("new_player", {}).get("data", {}).get("id")

            if not player_id:
                continue

            player_info = players.get(player_id, {}).get("attributes", {})

            player_name = player_info.get("name")
            stat_type = attr.get("stat_type")
            line = attr.get("line_score")

            if not player_name or line is None or not stat_type:
                continue

            props.append({
                "player": player_name,
                "stat": stat_type.lower(),
                "line": line
            })

        print(f"✅ PrizePicks props: {len(props)}")

        return props

    except Exception as e:
        print("❌ PRIZEPICKS ERROR:", e)
        return []