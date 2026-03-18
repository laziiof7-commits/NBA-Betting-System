# --------------------------------------------------
# 🔥 ELITE PROP MODEL (ML + SELF-LEARNING + MULTI-STAT)
# --------------------------------------------------

from player_data import project_points as real_points
from minutes_model import project_minutes
from usage_model import project_usage
from lineup_model import lineup_adjustment
from time_series_model import predict_trend
from nn_model import predict_nn

from model_optimizer import get_weights

# optional (safe import)
try:
    from prop_tracker import hit_rate
except:
    def hit_rate():
        return 0.55


# --------------------------------------------------
# 🧠 BASE MODEL (FEATURE GENERATOR)
# --------------------------------------------------

def base_model(player, stat, team=None, opponent=None, sentiment=0):

    minutes = project_minutes(player)
    usage = project_usage(player)
    trend = predict_trend(player)

    # -----------------------------
    # STAT-SPECIFIC RATES
    # -----------------------------
    if stat == "points":
        rate = 1.2
    elif stat == "rebounds":
        rate = 0.34
    elif stat == "assists":
        rate = 0.29
    else:
        rate = 1

    base_value = minutes * usage * rate

    # lineup impact
    if team and opponent:
        base_value += lineup_adjustment(team, opponent) * 0.12

    # sentiment + trend
    base_value += sentiment
    base_value += trend * 0.6

    # NN boost
    features = [minutes, usage, sentiment, trend, len(player)]
    nn_val = predict_nn(features)

    return {
        "base": base_value,
        "minutes": minutes,
        "usage": usage,
        "trend": trend,
        "nn": nn_val
    }


# --------------------------------------------------
# 📊 REAL DATA
# --------------------------------------------------

def real_stat(player, stat):

    if stat == "points":
        return real_points(player)

    return None


# --------------------------------------------------
# 🔥 HYBRID ML PROJECTION
# --------------------------------------------------

def project_stat(player, stat, team=None, opponent=None, sentiment=0):

    weights = get_weights()

    model_data = base_model(player, stat, team, opponent, sentiment)

    model_val = model_data["base"]
    trend = model_data["trend"]
    nn_val = model_data["nn"]

    real_val = real_stat(player, stat)

    # -----------------------------
    # ML WEIGHTED BLEND
    # -----------------------------
    if real_val is not None:
        projection = (
            real_val * weights["real"]
            + model_val * weights["model"]
            + trend * weights["trend"]
            + nn_val * weights["nn"]
        )
    else:
        projection = (
            model_val
            + trend * weights["trend"]
            + nn_val * weights["nn"]
        )

    return round(projection, 2), model_data


# --------------------------------------------------
# 📊 PRA MODEL
# --------------------------------------------------

def project_pra(player, team=None, opponent=None, sentiment=0):

    pts, _ = project_stat(player, "points", team, opponent, sentiment)
    reb, _ = project_stat(player, "rebounds", team, opponent, sentiment)
    ast, _ = project_stat(player, "assists", team, opponent, sentiment)

    return round(pts + reb + ast, 2)


# --------------------------------------------------
# 🎯 PROBABILITY MODEL (CALIBRATED)
# --------------------------------------------------

def calculate_probability(edge):

    base = 0.5 + (edge / 13)

    base = max(min(base, 0.82), 0.40)

    # performance feedback
    model_perf = hit_rate()

    adjusted = base * (0.6 + model_perf)

    return round(min(adjusted, 0.87), 3)


# --------------------------------------------------
# 💎 EDGE SCORE
# --------------------------------------------------

def calculate_score(edge):
    return round(abs(edge) * 13, 2)


# --------------------------------------------------
# 🔥 CONFIDENCE SYSTEM (UPGRADED)
# --------------------------------------------------

def calculate_confidence(score, probability):

    conf = (score / 100) * probability * 1.2

    return round(min(conf, 1), 2)


# --------------------------------------------------
# 🎯 MAIN EVALUATOR (ML READY)
# --------------------------------------------------

def evaluate_prop(player, line, stat="points", team=None, opponent=None, sentiment=0):

    try:

        # -----------------------------
        # PROJECTION
        # -----------------------------
        if stat == "pra":
            projection = project_pra(player, team, opponent, sentiment)
            model_data = {"trend": 0, "nn": 0}
        else:
            projection, model_data = project_stat(player, stat, team, opponent, sentiment)

        edge = projection - line

        probability = calculate_probability(edge)
        score = calculate_score(edge)
        confidence = calculate_confidence(score, probability)

        bet = "OVER" if edge > 0 else "UNDER"

        # 🔥 RETURN FULL ML FEATURE SET
        return {
            "player": player,
            "stat": stat.upper(),
            "line": line,
            "projection": projection,
            "edge": round(edge, 2),
            "probability": probability,
            "score": score,
            "confidence": confidence,
            "bet": bet,

            # -------------------------
            # 🔥 ML FEATURES (CRITICAL)
            # -------------------------
            "real": real_stat(player, stat) or 0,
            "model": model_data.get("base", 0),
            "trend": model_data.get("trend", 0),
            "nn": model_data.get("nn", 0)
        }

    except Exception as e:
        print("❌ PROP MODEL ERROR:", e)
        return None


# --------------------------------------------------
# 🎯 ELITE FILTER
# --------------------------------------------------

def is_good_prop(prop):

    if not prop:
        return False

    return (
        abs(prop["edge"]) > 3
        and prop["probability"] > 0.58
        and prop["score"] > 32
        and prop["confidence"] > 0.30
    )


# --------------------------------------------------
# 💰 BET SIZING BOOST
# --------------------------------------------------

def prop_bet_size(prop, base_size):

    if not prop:
        return 0

    multiplier = 1 + (prop["confidence"] * 0.7)

    return round(base_size * multiplier, 2)