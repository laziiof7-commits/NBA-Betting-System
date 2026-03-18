# --------------------------------------------------
# 🔥 ELITE ROLE + INJURY MODEL (DYNAMIC + API + SAFE)
# --------------------------------------------------

import time

# --------------------------------------------------
# SAFE IMPORT (INJURY API)
# --------------------------------------------------

try:
    from injury_api import get_injuries
except:
    def get_injuries(): return {}

# --------------------------------------------------
# PLAYER ROLE TIERS
# --------------------------------------------------

PLAYER_ROLES = {
    "LeBron James": "star",
    "Stephen Curry": "star",
    "Luka Doncic": "star",
    "Nikola Jokic": "star"
}

DEFAULT_ROLE = "secondary"

# --------------------------------------------------
# ROLE MULTIPLIERS
# --------------------------------------------------

ROLE_MULTIPLIER = {
    "star": 1.25,
    "primary": 1.15,
    "secondary": 1.0,
    "bench": 0.85
}

# --------------------------------------------------
# INJURY CACHE (PREVENT API SPAM)
# --------------------------------------------------

INJURY_CACHE = {}
LAST_FETCH = 0
CACHE_TTL = 300  # 5 minutes


def get_cached_injuries():

    global INJURY_CACHE, LAST_FETCH

    now = time.time()

    if now - LAST_FETCH > CACHE_TTL:
        try:
            INJURY_CACHE = get_injuries()
            LAST_FETCH = now
        except:
            INJURY_CACHE = {}

    return INJURY_CACHE


# --------------------------------------------------
# ROLE BOOST
# --------------------------------------------------

def role_boost(player):

    role = PLAYER_ROLES.get(player, DEFAULT_ROLE)
    multiplier = ROLE_MULTIPLIER.get(role, 1.0)

    # convert multiplier → additive boost
    return (multiplier - 1) * 10


# --------------------------------------------------
# INJURY IMPACT (SMART)
# --------------------------------------------------

def injury_boost(player, team=None):

    injuries = get_cached_injuries()

    if not injuries:
        return 0

    boost = 0

    for injured_player, status in injuries.items():

        # skip questionable players (low impact)
        if status and "Out" not in status:
            continue

        # basic teammate impact (can improve later)
        if team and injured_player != player:

            # star teammate out → big boost
            if injured_player in PLAYER_ROLES:
                boost += 2.5
            else:
                boost += 1.0

    return boost


# --------------------------------------------------
# USAGE SPIKE DETECTION (NEW 🔥)
# --------------------------------------------------

def usage_spike(player, injuries):

    spike = 0

    for injured_player in injuries:

        if injured_player == player:
            continue

        # if high-usage teammate out → spike
        if injured_player in PLAYER_ROLES:
            spike += 0.05

    return spike


# --------------------------------------------------
# FINAL ROLE + INJURY ADJUSTMENT
# --------------------------------------------------

def role_adjustment(player, team=None):

    try:
        # role base
        role_val = role_boost(player)

        # injury context
        injuries = get_cached_injuries()

        injury_val = injury_boost(player, team)

        # usage spike
        spike = usage_spike(player, injuries)

        # combine
        total = role_val + injury_val + (spike * 10)

        return round(total, 2)

    except Exception as e:
        print("❌ ROLE MODEL ERROR:", e)
        return 0
