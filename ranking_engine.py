# --------------------------------------------------
# 🏆 BET RANKING ENGINE
# --------------------------------------------------

def rank_bets(bets):

    for b in bets:

        edge = abs(b.get("edge", 0))
        prob = b.get("probability", 0)
        clv = b.get("clv", 0)

        # 🔥 weighted score
        score = (edge * 2) + (prob * 10) + (clv * 1.5)

        b["score"] = round(score, 2)

    return sorted(bets, key=lambda x: x["score"], reverse=True)