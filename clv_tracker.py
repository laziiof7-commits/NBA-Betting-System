# --------------------------------------------------
# 📈 CLV TRACKER (PRO MODE - FIXED + EXTENDED)
# --------------------------------------------------

import csv
import os
import json
from datetime import datetime

# --------------------------------------------------
# STORAGE
# --------------------------------------------------

CLV_DATA = []
LIVE_CLV = []
BET_HISTORY = []

PROP_CLV_STORE = {}

BET_LOG_FILE = "bet_history.csv"
JSON_LOG_FILE = "bet_history.json"

# --------------------------------------------------
# LOAD / SAVE
# --------------------------------------------------

def load_bets():

    if os.path.exists(JSON_LOG_FILE):
        with open(JSON_LOG_FILE, "r") as f:
            data = json.load(f)

            BET_HISTORY.clear()
            BET_HISTORY.extend(data)

    return BET_HISTORY


def save_all_bets():

    with open(JSON_LOG_FILE, "w") as f:
        json.dump(BET_HISTORY, f, indent=2)

# --------------------------------------------------
# 🔥 PROP CLV TRACKING (REAL-TIME ENGINE)
# --------------------------------------------------

def record_prop_line(player, stat, line):

    key = f"{player}-{stat}"

    if key not in PROP_CLV_STORE:
        PROP_CLV_STORE[key] = {
            "open_line": line,
            "history": [line],
            "clv": 0
        }


def update_prop_line(player, stat, new_line):

    key = f"{player}-{stat}"

    if key not in PROP_CLV_STORE:
        return 0

    PROP_CLV_STORE[key]["history"].append(new_line)

    open_line = PROP_CLV_STORE[key]["open_line"]
    clv = round(new_line - open_line, 2)

    PROP_CLV_STORE[key]["clv"] = clv

    return clv


def get_prop_clv(player, stat):

    key = f"{player}-{stat}"

    if key not in PROP_CLV_STORE:
        return 0

    return PROP_CLV_STORE[key].get("clv", 0)

# --------------------------------------------------
# PRE-GAME CLV (LEGACY)
# --------------------------------------------------

def record_clv(model_line, bet_line, closing_line):

    if closing_line is None:
        return

    clv = closing_line - bet_line

    CLV_DATA.append({
        "model": model_line,
        "bet": bet_line,
        "close": closing_line,
        "clv": round(clv, 2),
        "timestamp": datetime.now().isoformat()
    })

# --------------------------------------------------
# LIVE CLV
# --------------------------------------------------

def record_live_clv(bet_line, current_line):

    if current_line is None:
        return

    clv = current_line - bet_line
    LIVE_CLV.append(round(clv, 2))


def average_live_clv():

    if not LIVE_CLV:
        return 0

    return round(sum(LIVE_CLV) / len(LIVE_CLV), 2)

# --------------------------------------------------
# AVERAGES
# --------------------------------------------------

def average_clv():

    if not CLV_DATA:
        return 0

    return round(sum(x["clv"] for x in CLV_DATA) / len(CLV_DATA), 2)


def clv_quality():

    avg = average_clv()

    if avg > 2:
        return "🔥 ELITE"
    elif avg > 1:
        return "STRONG"
    elif avg > 0.3:
        return "STABLE"
    else:
        return "⚠️ NEGATIVE"

# --------------------------------------------------
# EDGE vs CLV CORRELATION
# --------------------------------------------------

def edge_clv_correlation():

    if len(CLV_DATA) < 5:
        return 0

    edges = [x["model"] - x["bet"] for x in CLV_DATA]
    clvs = [x["clv"] for x in CLV_DATA]

    try:
        import numpy as np
        return round(np.corrcoef(edges, clvs)[0, 1], 3)
    except:
        return 0

# --------------------------------------------------
# BET LOGGING
# --------------------------------------------------

def log_bet(game, bet_type, line, stake, model_line):

    bet = {
        "game": game,
        "bet_type": bet_type,
        "line": line,
        "stake": stake,
        "model_line": model_line,
        "result": None,
        "profit": 0,
        "closing_line": None,
        "clv": None,
        "timestamp": datetime.now().isoformat()
    }

    BET_HISTORY.append(bet)

    save_bet_to_csv(bet)
    save_all_bets()


def save_bet_to_csv(bet):

    file_exists = os.path.isfile(BET_LOG_FILE)

    with open(BET_LOG_FILE, "a", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=bet.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(bet)

# --------------------------------------------------
# UPDATE CLOSING LINES
# --------------------------------------------------

def update_closing_lines(api_games):

    for bet in BET_HISTORY:

        if bet["closing_line"] is not None:
            continue

        game = bet["game"]

        for date, games in api_games.items():

            for key, g in games.items():

                if game.lower() in key.lower():

                    close = g.get("market_total")

                    if close:
                        bet["closing_line"] = close

                        if bet["bet_type"] == "OVER":
                            bet["clv"] = round(close - bet["line"], 2)
                        else:
                            bet["clv"] = round(bet["line"] - close, 2)

    save_all_bets()

# --------------------------------------------------
# AUTO GRADING
# --------------------------------------------------

def grade_bet(actual_total):

    for bet in BET_HISTORY:

        if bet["result"] is not None:
            continue

        if bet["bet_type"] == "OVER":

            if actual_total > bet["line"]:
                bet["result"] = "WIN"
                bet["profit"] = bet["stake"] * 0.91
            else:
                bet["result"] = "LOSS"
                bet["profit"] = -bet["stake"]

        elif bet["bet_type"] == "UNDER":

            if actual_total < bet["line"]:
                bet["result"] = "WIN"
                bet["profit"] = bet["stake"] * 0.91
            else:
                bet["result"] = "LOSS"
                bet["profit"] = -bet["stake"]

    save_all_bets()

# --------------------------------------------------
# ROI
# --------------------------------------------------

def calculate_roi():

    if not BET_HISTORY:
        return {"roi": 0, "profit": 0}

    total_profit = sum(b["profit"] for b in BET_HISTORY)
    total_staked = sum(b["stake"] for b in BET_HISTORY)

    roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0

    return {
        "roi": round(roi, 2),
        "profit": round(total_profit, 2)
    }

# --------------------------------------------------
# PROFIT CURVE
# --------------------------------------------------

def profit_curve():

    curve = []
    running = 0

    for bet in BET_HISTORY:
        running += bet["profit"]
        curve.append(running)

    return curve

# --------------------------------------------------
# MODEL HEALTH
# --------------------------------------------------

def model_health():

    clv = average_clv()
    roi = calculate_roi()["roi"]

    if clv > 1.5 and roi > 5:
        return "🔥 ELITE"
    elif clv > 0.7 and roi > 2:
        return "STRONG"
    elif clv > 0:
        return "STABLE"
    else:
        return "⚠️ NEEDS ADJUSTMENT"

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def calculate_clv():

    return {
        "avg_clv": average_clv(),
        "live_clv": average_live_clv(),
        "quality": clv_quality(),
        "bets": len(BET_HISTORY),
        "correlation": edge_clv_correlation()
    }
