# --------------------------------------------------
# 🔥 ELITE PROP MODEL (FINAL + ROLE + MATCHUP + ML)
# --------------------------------------------------

# --------------------------------------------------
# ✅ SAFE IMPORTS (NO CRASHES)
# --------------------------------------------------

try:
    from player_data import project_points as real_points
except:
    def real_points(player): return None

try:
    from minutes_model import project_minutes
except:
    def project_minutes(player): return 30

try:
    from usage_model import project_usage
except:
    def project_usage(player): return 0.22

try:
    from lineup_model import lineup_adjustment
except:
    def lineup_adjustment(a, b): return 0

try:
    from time_series_model import predict_trend
except:
    def predict_trend(player): return 0

try:
    from nn_model import predict_nn
except:
    def predict_nn(features): return 0

try:
    from model_optimizer import get_weights
except:
    def get_weights():
        return {
            "real": 0.5,
            "model": 0.3,
            "trend": 0.1,
            "nn": 0.1
        }

try:
    from prop_tracker import hit_rate
except:
    def hit_rate(): return 0.55

# 🔥 NEW MODELS
try:
    from matchup_model import matchup_boost
except:
    def matchup_boost(*args, **kwargs): return 0

try:
    from role_model import role_adjustment
except:
    def role_adjustment(*args, **kwargs): return 0


# --------------------------------------------------
# 🧠 BASE FEATURE ENGINE
# --------------------------------------------------

def base_model(player, stat, team=None, opponent=None, sentiment=0):

    minutes = project_minutes(player)
    usage = project_usage(player)
    trend = predict_trend(player)

    # -----------------------------
    # STAT RATES
    # -----------------------------
    stat_rates = {
        "points": 1.2,
        "rebounds": 0.34,
        "assists": 0.29
    }

    rate = stat_rates.get(stat, 1)

    # -----------------------------
    # CORE PROJECTION
    # -----------------------------
    base_val = minutes * usage * rate

    # 🔥 ROLE + INJURY BOOST
    base_val += role_adjustment(player, team)

    # 🔥 MATCHUP BOOST
    if team and opponent:
        base_val += matchup_boost(player, stat, team, opponent)

    # lineup impact
    if team and opponent:
        base_val += lineup_adjustment(team, opponent) * 0.12

    # sentiment + trend
    base_val += sentiment
    base_val += trend * 0.6

    # -----------------------------
    # NN LAYER
    # -----------------------------
    features = [minutes, usage, sentiment, trend, len(player)]
    nn_val = predict_nn(features)

    return {
        "base": base_val,
        "trend": trend,
        "nn": nn_val,
        "minutes": minutes,
        "usage": usage
    }


# --------------------------------------------------
# 📊 REAL DATA
# --------------------------------------------------

def real_stat(player, stat):

    if stat == "points":
        return real_points(player)

    return None


# --------------------------------------------------
# 🔥 PROJECTION ENGINE (ML BLEND)
# --------------------------------------------------

def project_stat(player, stat, team=None, opponent=None, sentiment=0):

    weights = get_weights()

    model = base_model(player, stat, team, opponent, sentiment)

    base = model["base"]
    trend = model["trend"]
    nn_val = model["nn"]

    real = real_stat(player, stat)

    # -----------------------------
    # ML WEIGHTED BLEND
    # -----------------------------
    if real is not None:
        projection = (
            real * weights["real"]
            + base * weights["model"]
            + trend * weights["trend"]
            + nn_val * weights["nn"]
        )
    else:
        projection = base + trend * weights["trend"] + nn_val * weights["nn"]

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
# 🎯 PROBABILITY MODEL (ADAPTIVE)
# --------------------------------------------------

def calculate_probability(edge):

    base = 0.5 + (edge / 14)

    base = max(min(base, 0.82), 0.40)

    perf = hit_rate()

    adjusted = base * (0.6 + perf)

    return round(min(adjusted, 0.88), 3)


# --------------------------------------------------
# 💎 EDGE SCORE
# --------------------------------------------------

def calculate_score(edge):
    return round(abs(edge) * 14, 2)


# --------------------------------------------------
# 🔥 CONFIDENCE MODEL
# --------------------------------------------------

def calculate_confidence(score, probability):

    conf = (score / 100) * probability * 1.25

    return round(min(conf, 1), 2)


# --------------------------------------------------
# 🎯 MAIN PROP EVALUATOR
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

            # 🔥 ML FEATURES
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
        and prop["score"] > 30
        and prop["confidence"] > 0.30
    )


# --------------------------------------------------
# 💰 BET SIZING
# --------------------------------------------------

def prop_bet_size(prop, base_size=10):

    if not prop:
        return 0

    multiplier = 1 + (prop["confidence"] * 0.7)

    return round(base_size * multiplier, 2)
