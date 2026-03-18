# --------------------------------------------------
# 🔥 AUTO GRADING (REAL DATA)
# --------------------------------------------------

import requests

def fetch_player_stats():

    try:
        url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/scoreboard"

        res = requests.get(url, timeout=6)
        data = res.json()

        results = {}

        for game in data.get("events", []):

            for team in game.get("competitions", [])[0].get("competitors", []):

                athletes = team.get("athletes", [])

                for p in athletes:

                    name = p.get("athlete", {}).get("displayName")

                    stats = p.get("statistics", [])

                    if not name or not stats:
                        continue

                    stat_map = {
                        "points": None,
                        "rebounds": None,
                        "assists": None
                    }

                    for s in stats:
                        label = s.get("name", "").lower()
                        val = s.get("displayValue")

                        try:
                            val = float(val)
                        except:
                            continue

                        if "points" in label:
                            stat_map["points"] = val
                        elif "rebounds" in label:
                            stat_map["rebounds"] = val
                        elif "assists" in label:
                            stat_map["assists"] = val

                    results[name] = stat_map

        return results

    except Exception as e:
        print("❌ STATS FETCH ERROR:", e)
        return {}
