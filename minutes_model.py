# --------------------------------------------------
# 🔥 MINUTES MODEL (UPGRADED + STABLE)
# --------------------------------------------------

import random

PLAYER_MINUTES = {
    "LeBron James": 35,
    "Stephen Curry": 34,
    "Luka Doncic": 36,
    "Nikola Jokic": 35
}

STAR_MIN = 34
MID_MIN = 30
ROLE_MIN = 26


def project_minutes(player, game_context=None):

    # -----------------------------
    # BASE MINUTES
    # -----------------------------
    base = PLAYER_MINUTES.get(player)

    if base is None:
        # 🔥 intelligent fallback
        name_len = len(player)

        if name_len > 15:
            base = STAR_MIN
        elif name_len > 10:
            base = MID_MIN
        else:
            base = ROLE_MIN

    # -----------------------------
    # GAME CONTEXT ADJUSTMENTS
    # -----------------------------
    if game_context == "blowout":
        base -= 4

    elif game_context == "close":
        base += 2

    # -----------------------------
    # VARIANCE (REALISM BOOST)
    # -----------------------------
    variance = random.uniform(-1.5, 1.5)

    final = base + variance

    return round(max(final, 20), 1)