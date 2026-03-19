# --------------------------------------------------
# 💰 BANKROLL MANAGER (CLV + EDGE AWARE)
# --------------------------------------------------

MAX_BET = 0.03

def kelly(prob, odds=1.91):

    b = odds - 1
    q = 1 - prob

    k = ((b * prob) - q) / b

    return max(k, 0)

def get_bet_size(probability, edge_score, bankroll, clv=0):

    if probability is None:
        return 0

    k = kelly(probability)

    # 🔥 EDGE BOOST
    k *= min(edge_score / 100, 1)

    # 🔥 CLV BOOST
    if clv > 1:
        k *= 1.2
    elif clv < 0:
        k *= 0.8

    # HALF KELLY
    k *= 0.5

    k = min(k, MAX_BET)

    return round(bankroll * k, 2)
