# --------------------------------------------------
# 📈 CLV TRACKER (REAL-TIME + PROP LEVEL)
# --------------------------------------------------

import json
import os
from datetime import datetime

CLV_STORE = {}
CLV_HISTORY = []

FILE = "clv_data.json"

# ---------------- LOAD ----------------

def load_clv():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = json.load(f)
            CLV_STORE.update(data.get("store", {}))
            CLV_HISTORY.extend(data.get("history", []))

# ---------------- SAVE ----------------

def save_clv():
    with open(FILE, "w") as f:
        json.dump({
            "store": CLV_STORE,
            "history": CLV_HISTORY
        }, f, indent=2)

# ---------------- RECORD LINE ----------------

def record_prop_line(player, stat, line):

    key = f"{player}-{stat}"

    if key not in CLV_STORE:
        CLV_STORE[key] = {
            "open": line,
            "last": line
        }
    else:
        CLV_STORE[key]["last"] = line

# ---------------- UPDATE CLV ----------------

def update_prop_line(player, stat, current_line):

    key = f"{player}-{stat}"

    data = CLV_STORE.get(key)

    if not data:
        return 0

    open_line = data["open"]

    clv = current_line - open_line

    CLV_HISTORY.append({
        "key": key,
        "open": open_line,
        "current": current_line,
        "clv": round(clv, 2),
        "time": datetime.utcnow().isoformat()
    })

    return round(clv, 2)

# ---------------- STATS ----------------

def calculate_clv():

    if not CLV_HISTORY:
        return {"avg_clv": 0, "count": 0}

    avg = sum(x["clv"] for x in CLV_HISTORY) / len(CLV_HISTORY)

    return {
        "avg_clv": round(avg, 2),
        "count": len(CLV_HISTORY)
    }

# ---------------- ROI ----------------

BET_RESULTS = []

def record_result(profit):
    BET_RESULTS.append(profit)

def calculate_roi():

    if not BET_RESULTS:
        return {"roi": 0, "profit": 0}

    total = sum(BET_RESULTS)
    stake = len(BET_RESULTS) * 100

    roi = (total / stake) * 100 if stake else 0

    return {
        "roi": round(roi, 2),
        "profit": round(total, 2)
    }

# ---------------- HEALTH ----------------

def model_health():

    clv = calculate_clv()["avg_clv"]
    roi = calculate_roi()["roi"]

    if clv > 1 and roi > 5:
        return "🔥 ELITE"
    elif clv > 0.5:
        return "STRONG"
    elif clv > 0:
        return "STABLE"
    else:
        return "⚠️ NEGATIVE"
