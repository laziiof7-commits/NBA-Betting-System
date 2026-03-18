# --------------------------------------------------
# BANKROLL MANAGER (FINAL FORM)
# --------------------------------------------------

# --------------------------------------------------
# DEFAULT SETTINGS
# --------------------------------------------------

DEFAULT_DECIMAL_ODDS = 1.91
DEFAULT_BANKROLL = 1000.0

MAX_BET_FRACTION = 0.05      # max 5% bankroll on any one bet
HALF_KELLY_MULTIPLIER = 0.5  # safer than full Kelly
MIN_EDGE_SCORE = 70
MIN_PROBABILITY = 0.57
MIN_CLV_EDGE = 0.0


# --------------------------------------------------
# CORE KELLY FRACTION
# --------------------------------------------------

def kelly_fraction(probability, decimal_odds=DEFAULT_DECIMAL_ODDS):
    """
    Full Kelly fraction using decimal odds.
    Example:
        probability = 0.58
        decimal_odds = 1.91
    """

    if probability is None:
        return 0.0

    if probability <= 0 or probability >= 1:
        return 0.0

    if decimal_odds <= 1:
        return 0.0

    b = decimal_odds - 1
    q = 1 - probability

    kelly = ((b * probability) - q) / b

    return max(kelly, 0.0)


# --------------------------------------------------
# SAFE KELLY
# --------------------------------------------------

def safe_kelly_fraction(
    probability,
    edge_score=None,
    decimal_odds=DEFAULT_DECIMAL_ODDS,
    half_kelly=HALF_KELLY_MULTIPLIER,
    max_fraction=MAX_BET_FRACTION
):
    """
    Safer Kelly sizing:
    - starts from full Kelly
    - uses half Kelly
    - scales by edge score
    - caps risk
    """

    base_kelly = kelly_fraction(probability, decimal_odds)

    if base_kelly <= 0:
        return 0.0

    scaled = base_kelly * half_kelly

    if edge_score is not None:
        score_scale = min(max(edge_score / 100, 0.0), 1.0)
        scaled *= score_scale

    return round(min(scaled, max_fraction), 4)


# --------------------------------------------------
# BET SIZE ENGINE
# --------------------------------------------------

def get_bet_size(
    probability,
    edge_score=None,
    bankroll=DEFAULT_BANKROLL,
    decimal_odds=DEFAULT_DECIMAL_ODDS
):
    """
    Returns dollar stake based on bankroll and safe Kelly.
    """

    if bankroll is None or bankroll <= 0:
        return 0.0

    fraction = safe_kelly_fraction(
        probability=probability,
        edge_score=edge_score,
        decimal_odds=decimal_odds
    )

    stake = bankroll * fraction

    return round(stake, 2)


# --------------------------------------------------
# FLAT BET FALLBACK
# --------------------------------------------------

def flat_bet_size(bankroll=DEFAULT_BANKROLL, fraction=0.01):
    """
    Optional flat sizing fallback.
    Example: 1% bankroll per bet.
    """

    if bankroll is None or bankroll <= 0:
        return 0.0

    return round(bankroll * fraction, 2)


# --------------------------------------------------
# BET FILTER
# --------------------------------------------------

def should_bet(
    edge_score,
    probability,
    clv_edge=0.0,
    min_edge_score=MIN_EDGE_SCORE,
    min_probability=MIN_PROBABILITY,
    min_clv_edge=MIN_CLV_EDGE
):
    """
    Final betting gate.
    Only allows strong, +EV, CLV-supported bets.
    """

    if edge_score is None or probability is None:
        return False

    if edge_score < min_edge_score:
        return False

    if probability < min_probability:
        return False

    if clv_edge < min_clv_edge:
        return False

    return True


# --------------------------------------------------
# ELITE MODE FILTER
# --------------------------------------------------

def elite_bet_only(edge_score, probability, clv_edge=0.0):
    """
    Stricter version for top-tier bets only.
    """

    return should_bet(
        edge_score=edge_score,
        probability=probability,
        clv_edge=clv_edge,
        min_edge_score=80,
        min_probability=0.60,
        min_clv_edge=0.25
    )


# --------------------------------------------------
# BANKROLL UPDATE
# --------------------------------------------------

def update_bankroll(current_bankroll, profit):
    """
    Applies bet result profit/loss to bankroll.
    """

    if current_bankroll is None:
        current_bankroll = DEFAULT_BANKROLL

    return round(current_bankroll + profit, 2)


# --------------------------------------------------
# PROFIT CALCULATOR
# --------------------------------------------------

def calculate_profit(stake, result, price=-110):
    """
    Calculates profit from a settled bet.

    result:
        WIN / LOSS / PUSH
    """

    if stake is None or stake <= 0:
        return 0.0

    result = str(result).upper()

    if result == "WIN":
        if price < 0:
            return round(stake * (100 / abs(price)), 2)
        return round(stake * (price / 100), 2)

    if result == "LOSS":
        return round(-stake, 2)

    return 0.0


# --------------------------------------------------
# DRAWDOWN GUARD
# --------------------------------------------------

def drawdown_adjustment(bankroll, peak_bankroll):
    """
    Reduce aggression during drawdowns.
    Returns multiplier between 0.5 and 1.0.
    """

    if bankroll is None or peak_bankroll is None or peak_bankroll <= 0:
        return 1.0

    drawdown = (peak_bankroll - bankroll) / peak_bankroll

    if drawdown >= 0.20:
        return 0.5
    elif drawdown >= 0.10:
        return 0.75

    return 1.0


# --------------------------------------------------
# ADJUSTED BET SIZE WITH DRAWDOWN CONTROL
# --------------------------------------------------

def get_adjusted_bet_size(
    probability,
    edge_score=None,
    bankroll=DEFAULT_BANKROLL,
    peak_bankroll=None,
    decimal_odds=DEFAULT_DECIMAL_ODDS
):
    """
    Kelly size with drawdown protection.
    """

    raw_bet = get_bet_size(
        probability=probability,
        edge_score=edge_score,
        bankroll=bankroll,
        decimal_odds=decimal_odds
    )

    multiplier = drawdown_adjustment(bankroll, peak_bankroll or bankroll)

    return round(raw_bet * multiplier, 2)


# --------------------------------------------------
# SUMMARY HELPER
# --------------------------------------------------

def bankroll_summary(
    bankroll,
    peak_bankroll=None,
    probability=None,
    edge_score=None
):
    """
    Useful for UI / diagnostics.
    """

    return {
        "bankroll": round(bankroll, 2) if bankroll is not None else DEFAULT_BANKROLL,
        "peak_bankroll": round(peak_bankroll, 2) if peak_bankroll is not None else None,
        "drawdown_multiplier": drawdown_adjustment(bankroll, peak_bankroll or bankroll),
        "kelly_fraction": safe_kelly_fraction(probability, edge_score),
        "recommended_bet": get_adjusted_bet_size(
            probability=probability,
            edge_score=edge_score,
            bankroll=bankroll,
            peak_bankroll=peak_bankroll
        ) if probability is not None else 0.0
    }