# --------------------------------------------------
# 🔥 PROP MODEL (FINAL WORKING VERSION)
# --------------------------------------------------

def safe_import(module, func, default):
    try:
        m = __import__(module, fromlist=[func])
        return getattr(m, func)
    except:
        return default

project_minutes = safe_import("minutes_model", "project_minutes", lambda p: 34)
project_usage = safe_import("usage_model", "project_usage", lambda p: 0.25)

# --------------------------------------------------
# BASELINES
# --------------------------------------------------

BASELINES = {
"points": 30, # 🔥 was too low
"rebounds": 9,
"assists": 7
}

# --------------------------------------------------
# ADJUSTMENT
# --------------------------------------------------

def adjust(player, minutes, usage):

    min_factor = minutes / 34
    usage_factor = usage / 0.25

    if usage > 0.30:
        usage_factor *= 1.08

    return min_factor * usage_factor

# --------------------------------------------------
# PROJECTION
# --------------------------------------------------

def project(player, stat):

    minutes = project_minutes(player)
    usage = project_usage(player)

    base = BASELINES.get(stat, 10)

    projection = base * adjust(player, minutes, usage)

    # final calibration
    projection *= 0.76

    return round(projection, 2)

# --------------------------------------------------
# EVALUATE
# --------------------------------------------------

def evaluate_prop(player, line, stat="points", **kwargs):

    try:
        projection = project(player, stat)
        edge = projection - line

        # 🔥 FINAL PROBABILITY FIX
        probability = max(min(0.5 + edge / 9, 0.85), 0.45)

        confidence = min((abs(edge) / 8) * probability, 1)

        return {
            "player": player,
            "stat": stat,
            "line": line,
            "projection": projection,
            "edge": round(edge, 2),
            "probability": round(probability, 3),
            "confidence": round(confidence, 2),
            "bet": "OVER" if edge > 0 else "UNDER"
        }

    except Exception as e:
        print("❌ MODEL ERROR:", e)
        return None

# --------------------------------------------------
# FILTER
# --------------------------------------------------

def is_good_prop(prop):

if not prop:
return False

return (
abs(prop["edge"]) > 1.0
and prop["probability"] > 0.55
and prop["confidence"] > 0.20
)

    if not prop:
        return False

    return (
        1.2 < abs(prop["edge"]) < 4
        and prop["probability"] > 0.58
        and prop["confidence"] > 0.30
    )

# --------------------------------------------------
# BET SIZE
# --------------------------------------------------

def prop_bet_size(prop, base_size=10):

    if not prop:
        return 0

    return round(base_size * (1 + prop["confidence"]), 2)
