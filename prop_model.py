# --------------------------------------------------
# 🔥 PROP MODEL (FIXED + STABLE)
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
# BASELINES (MORE REALISTIC)
# --------------------------------------------------

BASELINES = {
    "points": 26,
    "rebounds": 8,
    "assists": 6
}

# --------------------------------------------------
# ADJUSTMENT
# --------------------------------------------------

def adjust(player, minutes, usage):

    min_factor = minutes / 34
    usage_factor = usage / 0.25

    if usage > 0.30:
        usage_factor *= 1.10

    return min_factor * usage_factor

# --------------------------------------------------
# PROJECTION
# --------------------------------------------------

def project(player, stat):

    minutes = project_minutes(player)
    usage = project_usage(player)

    base = BASELINES.get(stat, 10)

    projection = base * adjust(player, minutes, usage)

    # 🔥 LESS COMPRESSION (CRITICAL FIX)
    projection *= 0.92

    return round(projection, 2)

# --------------------------------------------------
# EVALUATE
# --------------------------------------------------

def evaluate_prop(player, line, stat="points", **kwargs):

    try:
        projection = project(player, stat)
        edge = projection - line

        # 🔥 STRONGER PROBABILITY SPREAD
        probability = max(min(0.5 + edge / 7, 0.90), 0.40)

        confidence = min((abs(edge) / 6) * probability, 1)

        return {
            "player": player,
            "stat": stat,
            "line": line,
            "projection": projection,
            "edge": round(edge, 2),
            "probability": round(probability, 3),
            "confidence": round(confidence, 2),
            "score": round(abs(edge) * 10, 2),  # 🔥 IMPORTANT
            "bet": "OVER" if edge > 0 else "UNDER"
        }

    except Exception as e:
        print("❌ MODEL ERROR:", e)
        return None

# --------------------------------------------------
# FILTER (CLEAN + SINGLE LOGIC)
# --------------------------------------------------

def is_good_prop(prop):

    if not prop:
        return False

    return (
        abs(prop["edge"]) > 0.6
        and prop["probability"] > 0.52
        and prop["confidence"] > 0.15
    )

# --------------------------------------------------
# BET SIZE
# --------------------------------------------------

def prop_bet_size(prop, base_size=10):

    if not prop:
        return 0

    return round(base_size * (1 + prop["confidence"]), 2)
