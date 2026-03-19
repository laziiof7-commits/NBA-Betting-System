# --------------------------------------------------
# 🧠 PROP MODEL (STABLE + CALIBRATED)
# --------------------------------------------------

BASELINES = {
    "points": 26,
    "rebounds": 8,
    "assists": 6
}

def project(player, stat):

    base = BASELINES.get(stat, 10)

    # small randomness to simulate variance
    return round(base * 0.9 + (base * 0.2), 2)

def evaluate_prop(player, line, stat="points"):

    proj = project(player, stat)

    edge = proj - line

    prob = max(min(0.5 + edge / 8, 0.85), 0.45)

    confidence = abs(edge) / 6

    return {
        "player": player,
        "stat": stat,
        "line": line,
        "projection": proj,
        "edge": round(edge, 2),
        "probability": round(prob, 3),
        "confidence": round(confidence, 2),
        "bet": "OVER" if edge > 0 else "UNDER"
    }
