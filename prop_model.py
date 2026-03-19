# --------------------------------------------------
# 🔥 PROP MODEL (CALIBRATED + FIXED)
# --------------------------------------------------

def safe_import(module, func, default):
    try:
        m = __import__(module, fromlist=[func])
        return getattr(m, func)
    except:
        return default

project_minutes = safe_import("minutes_model", "project_minutes", lambda p: 32)
project_usage = safe_import("usage_model", "project_usage", lambda p: 0.25)

# --------------------------------------------------
# BASE MODEL
# --------------------------------------------------

def base_projection(player, stat):

    minutes = project_minutes(player)
    usage = project_usage(player)

    rates = {
        "points": 1.45,
        "rebounds": 0.42,
        "assists": 0.38
    }

    rate = rates.get(stat, 1)

    return minutes * usage * rate

# --------------------------------------------------
# MAIN PROJECTION
# --------------------------------------------------

def project(player, stat):

    base = base_projection(player, stat)

    # 🔥 GLOBAL BOOST (CRITICAL FIX)
    base *= 1.15

    return round(base, 2)

# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

def evaluate_prop(player, line, stat="points", **kwargs):

    try:

        projection = project(player, stat)

        edge = projection - line

        probability = max(min(0.5 + edge / 10, 0.85), 0.45)

        confidence = min((abs(edge) / 10) * probability, 1)

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
# FILTER (FIXED)
# --------------------------------------------------

def is_good_prop(prop):

    if not prop:
        return False

    return (
        abs(prop["edge"]) > 2
        and prop["probability"] > 0.58
        and prop["confidence"] > 0.25
    )

# --------------------------------------------------
# BET SIZE
# --------------------------------------------------

def prop_bet_size(prop, base_size=10):

    if not prop:
        return 0

    return round(base_size * (1 + prop["confidence"]), 2)
    # star players = higher stability
    if usage > 0.30:
        return 1.08

    # low usage = lower trust
    if usage < 0.20:
        return 0.92

    # minutes boost
    if minutes > 35:
        return 1.05

    return 1.0

# --------------------------------------------------
# 🧠 BASE FEATURE MODEL
# --------------------------------------------------

def base_model(player, stat, team=None, opponent=None, sentiment=0):

    minutes = project_minutes(player)
    usage = project_usage(player)
    trend = predict_trend(player)

    stat_rates = {
        "points": 1.15,
        "rebounds": 0.33,
        "assists": 0.28
    }

    rate = stat_rates.get(stat, 1)

    base = minutes * usage * rate

    # lineup impact
    if team and opponent:
        base += lineup_adjustment(team, opponent) * 0.1

    # trend + sentiment
    base += trend * 0.5
    base += sentiment

    # role adjustment
    role_mult = role_adjustment(player, minutes, usage)
    base *= role_mult

    # neural net
    features = [minutes, usage, trend, sentiment, len(player)]
    nn_val = predict_nn(features)

    return {
        "base": base,
        "trend": trend,
        "nn": nn_val,
        "minutes": minutes,
        "usage": usage
    }

# --------------------------------------------------
# 📊 REAL STAT
# --------------------------------------------------

def real_stat(player, stat):

    if stat == "points":
        return real_points(player)

    return None

# --------------------------------------------------
# 🔥 PROJECTION ENGINE (IMPROVED)
# --------------------------------------------------

def project_stat(player, stat, team=None, opponent=None, sentiment=0):

    weights = get_weights()

    model = base_model(player, stat, team, opponent, sentiment)

    base = model["base"]
    trend = model["trend"]
    nn_val = model["nn"]

    real = real_stat(player, stat)

    # normalize weights (prevents explosion)
    total_w = sum(weights.values())
    if total_w == 0:
        total_w = 1

    if real is not None:
        projection = (
            real * weights["real"] +
            base * weights["model"] +
            trend * weights["trend"] +
            nn_val * weights["nn"]
        ) / total_w
    else:
        projection = (
            base +
            trend * weights["trend"] +
            nn_val * weights["nn"]
        )

    return round(projection, 2), model

# --------------------------------------------------
# 📊 PRA MODEL
# --------------------------------------------------

def project_pra(player, team=None, opponent=None, sentiment=0):

    pts, _ = project_stat(player, "points", team, opponent, sentiment)
    reb, _ = project_stat(player, "rebounds", team, opponent, sentiment)
    ast, _ = project_stat(player, "assists", team, opponent, sentiment)

    return round(pts + reb + ast, 2)

# --------------------------------------------------
# 🎯 PROBABILITY (FIXED — WAS TOO LOW)
# --------------------------------------------------

def calculate_probability(edge):

    # improved scaling
    base = 0.5 + (edge / 10)

    base = max(min(base, 0.85), 0.42)

    perf = hit_rate()

    adjusted = base * (0.65 + perf)

    return round(min(adjusted, 0.9), 3)

# --------------------------------------------------
# 💎 EDGE SCORE
# --------------------------------------------------

def calculate_score(edge):
    return round(abs(edge) * 12, 2)

# --------------------------------------------------
# 🔥 CONFIDENCE
# --------------------------------------------------

def calculate_confidence(score, probability):

    conf = (score / 100) * probability * 1.3

    return round(min(conf, 1), 2)

# --------------------------------------------------
# 🎯 MAIN EVALUATOR
# --------------------------------------------------

def evaluate_prop(player, line, stat="points", team=None, opponent=None, sentiment=0):

    try:

        if stat == "pra":
            projection = project_pra(player, team, opponent, sentiment)
            model_data = {"base": 0, "trend": 0, "nn": 0}
        else:
            projection, model_data = project_stat(player, stat, team, opponent, sentiment)

        edge = projection - line

        probability = calculate_probability(edge)
        score = calculate_score(edge)
        confidence = calculate_confidence(score, probability)

        bet = "OVER" if edge > 0 else "UNDER"

        return {
            "player": player,
            "stat": stat,
            "line": line,
            "projection": projection,
            "edge": round(edge, 2),
            "probability": probability,
            "score": score,
            "confidence": confidence,
            "bet": bet,

            # ML FEATURES
            "real": real_stat(player, stat) or 0,
            "model": model_data.get("base", 0),
            "trend": model_data.get("trend", 0),
            "nn": model_data.get("nn", 0)
        }

    except Exception as e:
        print("❌ PROP MODEL ERROR:", e)
        return None

# --------------------------------------------------
# 🎯 FILTER (FIXED — LESS TRASH PROPS)
# --------------------------------------------------

def is_good_prop(prop):

    if not prop:
        return False

    return (
        abs(prop["edge"]) > 2.5
        and prop["probability"] > 0.60
        and prop["confidence"] > 0.35
    )

# --------------------------------------------------
# 💰 BET SIZING
# --------------------------------------------------

def prop_bet_size(prop, base_size=10):

    if not prop:
        return 0

    multiplier = 1 + (prop["confidence"] * 0.8)

    return round(base_size * multiplier, 2)
