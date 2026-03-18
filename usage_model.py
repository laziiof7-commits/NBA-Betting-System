# --------------------------------------------------
# 🔥 DYNAMIC USAGE MODEL (REALISTIC)
# --------------------------------------------------

PLAYER_USAGE = {
    "LeBron James": 0.30,
    "Stephen Curry": 0.32,
    "Luka Doncic": 0.36,
    "Nikola Jokic": 0.31
}

# fallback tiers
STAR_USAGE = 0.30
MID_USAGE = 0.25
ROLE_USAGE = 0.20


def project_usage(player):

    if player in PLAYER_USAGE:
        return PLAYER_USAGE[player]

    # 🔥 simple intelligence
    name_len = len(player)

    if name_len > 15:
        return STAR_USAGE
    elif name_len > 10:
        return MID_USAGE
    else:
        return ROLE_USAGE
