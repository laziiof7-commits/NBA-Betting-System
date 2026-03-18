# --------------------------------------------------
# 🔥 ELITE PROP TRACKER (FULL ML + CLV SYSTEM)
# --------------------------------------------------

import json
import os
import uuid
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
# 🧠 LOG PROP (ML READY)
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

        # 🔥 ML FEATURES
        "real": prop.get("real", 0),
        "model": prop.get("model", 0),
        "trend": prop.get("trend", 0),
        "nn": prop.get("nn", 0),

        "timestamp": datetime.utcnow().isoformat(),

        # CLV
        "bet_line": prop["line"],
        "closing_line": None,
        "clv": None,

        # grading
        "result": None,
        "actual": None,

        # bankroll
        "stake": prop.get("stake", 1),
        "profit": 0
    }

    data.append(entry)
    save_history(data)


# --------------------------------------------------
# 🔄 LIVE CLV TRACKING
# --------------------------------------------------

def update_clv_from_props(current_props):

    data = load_history()

    for p in data:

        if p["result"] is not None:
            continue

        for cp in current_props:

            if (
                cp["player"] == p["player"]
                and cp["stat"].lower() == p["stat"].lower()
            ):

                new_line = cp["line"]

                p["closing_line"] = new_line
                p["clv"] = round(new_line - p["bet_line"], 2)

    save_history(data)


# --------------------------------------------------
# 🎯 AUTO GRADING
# --------------------------------------------------

def grade_props(results):

    """
    results format:
    {
        "LeBron James": {"points": 31, "rebounds": 8}
    }
    """

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


# --------------------------------------------------
# 📊 HIT RATE
# --------------------------------------------------

def hit_rate():

    data = load_history()

    results = [p for p in data if p["result"] in ["WIN", "LOSS"]]

    if not results:
        return 0.55

    wins = len([p for p in results if p["result"] == "WIN"])

    return round(wins / len(results), 3)


# --------------------------------------------------
# 🔥 RECENT HIT RATE
# --------------------------------------------------

def recent_hit_rate(last_n=20):

    data = load_history()

    recent = [p for p in data if p["result"] in ["WIN", "LOSS"]][-last_n:]

    if not recent:
        return 0.55

    wins = len([p for p in recent if p["result"] == "WIN"])

    return round(wins / len(recent), 3)


# --------------------------------------------------
# 💰 ROI
# --------------------------------------------------

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
# 📈 CLV ANALYTICS
# --------------------------------------------------

def average_clv():

    data = load_history()

    clvs = [p["clv"] for p in data if p["clv"] is not None]

    if not clvs:
        return 0

    return round(sum(clvs) / len(clvs), 2)


# --------------------------------------------------
# 🧠 EDGE PERFORMANCE
# --------------------------------------------------

def edge_buckets():

    data = load_history()
    buckets = {}

    for p in data:

        if p["result"] is None:
            continue

        bucket = round(p["edge"])

        if bucket not in buckets:
            buckets[bucket] = {"win": 0, "total": 0}

        buckets[bucket]["total"] += 1

        if p["result"] == "WIN":
            buckets[bucket]["win"] += 1

    return {
        k: round(v["win"] / v["total"], 2)
        for k, v in buckets.items()
        if v["total"] > 5
    }


# --------------------------------------------------
# 📊 SUMMARY
# --------------------------------------------------

def summary():

    return {
        "hit_rate": hit_rate(),
        "recent_hit_rate": recent_hit_rate(),
        "roi": roi(),
        "avg_clv": average_clv(),
        "edge_performance": edge_buckets()
    }
