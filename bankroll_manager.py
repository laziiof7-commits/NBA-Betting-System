# --------------------------------------------------
# 💰 ELITE BANKROLL MANAGER (UPGRADED)
# --------------------------------------------------

import math

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

DEFAULT_BANKROLL = 1000.0
DEFAULT_ODDS = 1.91

MAX_BET_FRACTION = 0.03
MAX_SLATE_RISK = 0.10

MIN_EDGE_SCORE = 15
MIN_PROB = 0.52
MIN_CLV = 0.0

MIN_BET_SIZE = 5.0  # 🔥 NEW (important)


# --------------------------------------------------
# KELLY
# --------------------------------------------------

def kelly_fraction(prob, odds=DEFAULT_ODDS):

    if prob is None or prob <= 0 or prob >= 1:
        return 0.0

    b = odds - 1
    q = 1 - prob

    k = ((b * prob) - q) / b

    return max(k, 0.0)


# --------------------------------------------------
# SAFE KELLY
# --------------------------------------------------

def safe_kelly(prob, edge_score=None, clv=0):

    k = kelly_fraction(prob)

    if k <= 0:
        return 0.0

    # half Kelly
    k *= 0.5

    # edge scaling
    if edge_score:
        k *= min(edge_score / 100, 1)

    # 🔥 CLV BOOST (NEW)
    if clv and clv > 0:
        k *= (1 + min(clv * 0.25, 0.5))  # capped boost

    return min(k, MAX_BET_FRACTION)


# --------------------------------------------------
# VOLATILITY
# --------------------------------------------------

def volatility_adjustment(volatility):

    if volatility is None:
        return 1.0

    if volatility > 12:
        return 0.7
    elif volatility > 8:
        return 0.85

    return 1.0


# --------------------------------------------------
# DRAWDOWN
# --------------------------------------------------

def drawdown_factor(bankroll, peak):

    if peak is None or peak == 0:
        return 1.0

    dd = (peak - bankroll) / peak

    if dd > 0.25:
        return 0.4
    elif dd > 0.15:
        return 0.6
    elif dd > 0.08:
        return 0.8

    return 1.0


# --------------------------------------------------
# STREAK
# --------------------------------------------------

def streak_factor(last_results):

    if not last_results:
        return 1.0

    wins = last_results.count("win")
    losses = last_results.count("loss")

    if wins >= 4:
        return 1.1
    if losses >= 4:
        return 0.7

    return 1.0


# --------------------------------------------------
# FINAL BET SIZE
# --------------------------------------------------

def get_bet_size(
    probability,
    edge_score,
    bankroll,
    clv=0,  # 🔥 NEW
    volatility=None,
    peak_bankroll=None,
    last_results=None
):

    if bankroll <= 0:
        return 0.0

    k = safe_kelly(probability, edge_score, clv)

    k *= volatility_adjustment(volatility)
    k *= drawdown_factor(bankroll, peak_bankroll or bankroll)
    k *= streak_factor(last_results or [])

    stake = bankroll * k

    # 🔥 MIN BET FILTER
    if stake < MIN_BET_SIZE:
        return 0.0

    return round(stake, 2)


# --------------------------------------------------
# PORTFOLIO CONTROL
# --------------------------------------------------

def cap_slates(bets, bankroll):

    total = sum(b.get("bet_size", 0) for b in bets)

    max_allowed = bankroll * MAX_SLATE_RISK

    if total <= max_allowed:
        return bets

    scale = max_allowed / total

    for b in bets:
        b["bet_size"] *= scale

    return bets


# --------------------------------------------------
# CORRELATION FILTER (SAFE FIX)
# --------------------------------------------------

def correlation_filter(bets):

    seen = set()
    filtered = []

    for b in bets:

        game = b.get("game")

        if not game or "@" not in game:
            filtered.append(b)
            continue

        team = game.split("@")[0]

        if team in seen:
            continue

        seen.add(team)
        filtered.append(b)

    return filtered


# --------------------------------------------------
# BET FILTER
# --------------------------------------------------

def should_bet(edge_score, probability, clv):

    if edge_score is None or probability is None:
        return False

    if edge_score < MIN_EDGE_SCORE:
        return False

    if probability < MIN_PROB:
        return False

    if clv < MIN_CLV:
        return False

    return True


# --------------------------------------------------
# PROFIT
# --------------------------------------------------

def calculate_profit(stake, result, odds=-110):

    if result == "win":
        return round(stake * 0.91, 2)

    if result == "loss":
        return -stake

    return 0.0


# --------------------------------------------------
# UPDATE BANKROLL
# --------------------------------------------------

def update_bankroll(bankroll, profit):

    return round(bankroll + profit, 2)
