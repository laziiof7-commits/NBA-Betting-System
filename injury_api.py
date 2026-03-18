# --------------------------------------------------
# 🔥 INJURY API (FREE SOURCE)
# --------------------------------------------------

import requests

URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"

CACHE = {}

def get_injuries():

    try:
        res = requests.get(URL, timeout=5)
        data = res.json()

        injuries = {}

        for item in data.get("injuries", []):

            player = item.get("athlete", {}).get("fullName")
            status = item.get("status")

            if player:
                injuries[player] = status

        return injuries

    except Exception as e:
        print("❌ INJURY API ERROR:", e)
        return {}