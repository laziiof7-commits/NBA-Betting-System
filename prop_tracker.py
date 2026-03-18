# --------------------------------------------------
# 🔥 ELITE PROP TRACKER (FULLY UPGRADED)
# --------------------------------------------------

import json
import os
import uuid
import requests
from datetime import datetime

FILE = "prop_history.json"

# --------------------------------------------------
# LOAD / SAVE
# --------------------------------------------------

def load_history():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_history(data):
    try:
        with open(FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("❌ SAVE ERROR:", e)

# --------------------------------------------------
# LOG PROP
# --------------------------------------------------

def log_prop(prop):

    data = load_history()

    # prevent duplicates
    for p in data:
        if (
            p["player"] == prop["player"]
            and p["stat"] == prop["stat"]
            and p["line"] == prop["line"]
            and p["result"] is None
        ):
            return

    entry = {
        "id": str(uuid.uuid4()),
        "player": prop["player"],
        "stat": prop["stat"],
        "line": prop["line"],
        "projection": prop["projection"],
        "edge": prop["edge"],
        "probability": prop["probability"],
        "confidence": prop.get("confidence", 0),
        "bet": prop["bet"],

        # ML FEATURES
        "real": prop.get("real", 0),
        "model": prop.get("model", 0),
        "trend": prop.get("trend", 0),
        "nn": prop.get("nn", 0),

        # tracking
        "timestamp": str(datetime.utcnow()),
        "bet_line": prop["line"],
        "closing_line": None,
        "clv": None,

        # grading
        "result": None,
        "actual": None,

        # bankroll
        "stake": prop.get("bet_size", 1),
        "profit": 0
    }

    data.append(entry)
    save_history(data)

# --------------------------------------------------
# ESPN STATS FETCH
# --------------------------------------------------

def fetch_player_stats():

    try:
        url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/scoreboard"
        res = requests.get(url, timeout=6)
        data = res.json()

        results = {}

        for game in data.get("events", []):

            competitions = game.get("competitions", [])
            if not competitions:
                continue

            for team in competitions[0].get("competitors", []):

                for athlete in team.get("athletes", []):

                    name = athlete.get("athlete", {}).get("displayName")
                    stats = athlete.get("statistics", [])

                    if not name or not stats:
                        continue

                    stat_map = {}

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

# --------------------------------------------------
# AUTO GRADING
# --------------------------------------------------

def grade_props(results):

    data = load_history()

    for p in data:

        if p["result"] is not None:
            continue

        player = p["player"]
        stat = p["stat"].lower()

        if player not in results:
            continue

        actual = results[player].get(stat)

        if actual is None:
            continue

        p["actual"] = actual

        if p["bet"] == "OVER":
            win = actual > p["line"]
        else:
            win = actual < p["line"]

        p["result"] = "WIN" if win else "LOSS"

        stake = p.get("stake", 1)

        if win:
            p["profit"] = round(stake * 0.91, 2)
        else:
            p["profit"] = -stake

    save_history(data)

def auto_grade():

    stats = fetch_player_stats()

    if not stats:
        print("❌ No stats available")
        return

    grade_props(stats)

    print("✅ AUTO GRADING COMPLETE")

# --------------------------------------------------
# CLV TRACKING
# --------------------------------------------------

def update_clv(player, stat, current_line):

    data = load_history()

    for p in data:

        if p["result"] is not None:
            continue

        if p["player"] == player and p["stat"] == stat:

            p["closing_line"] = current_line
            p["clv"] = round(current_line - p["bet_line"], 2)

    save_history(data)

def average_clv():

    data = load_history()
    clvs = [p["clv"] for p in data if p["clv"] is not None]

    if not clvs:
        return 0

    return round(sum(clvs) / len(clvs), 2)

# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

def hit_rate():

    data = load_history()
    results = [p for p in data if p["result"] in ["WIN", "LOSS"]]

    if not results:
        return 0.55

    wins = len([p for p in results if p["result"] == "WIN"])

    return round(wins / len(results), 3)

def recent_hit_rate(n=20):

    data = load_history()
    recent = [p for p in data if p["result"] in ["WIN", "LOSS"]][-n:]

    if not recent:
        return 0.55

    wins = len([p for p in recent if p["result"] == "WIN"])

    return round(wins / len(recent), 3)

def roi():

    data = load_history()
    bets = [p for p in data if p["result"] is not None]

    if not bets:
        return {"roi": 0, "profit": 0}

    total_profit = sum(p["profit"] for p in bets)
    total_staked = sum(p.get("stake", 1) for p in bets)

    roi_val = (total_profit / total_staked) * 100

    return {
        "roi": round(roi_val, 2),
        "profit": round(total_profit, 2)
    }

# --------------------------------------------------
# SUMMARY DASHBOARD
# --------------------------------------------------

def summary():

    return {
        "hit_rate": hit_rate(),
        "recent_hit_rate": recent_hit_rate(),
        "roi": roi(),
        "avg_clv": average_clv(),
    }
