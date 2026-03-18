# --------------------------------------------------
# 🔥 PLAYER ROLE + INJURY MODEL
# --------------------------------------------------

# --------------------------------------------------
# PLAYER ROLES
# --------------------------------------------------

PLAYER_ROLES = {
    "LeBron James": "primary",
    "Stephen Curry": "primary",
    "Luka Doncic": "primary",
    "Nikola Jokic": "primary"
}

# fallback role
DEFAULT_ROLE = "secondary"

# role multipliers
ROLE_USAGE = {
    "primary": 1.15,
    "secondary": 1.0,
    "bench": 0.85
}


# --------------------------------------------------
# INJURY IMPACT (TEAM LEVEL)
# --------------------------------------------------

TEAM_INJURIES = {
    # "Lakers": ["Anthony Davis"]
}

# usage boost when teammate out
INJURY_BOOST = 0.08


# --------------------------------------------------
# ROLE BOOST
# --------------------------------------------------

def role_boost(player):

    role = PLAYER_ROLES.get(player, DEFAULT_ROLE)

    return ROLE_USAGE.get(role, 1.0)


# --------------------------------------------------
# INJURY BOOST
# --------------------------------------------------

def injury_boost(player, team):

    if not team:
        return 0

    team_name = team.split()[-1]

    injured = TEAM_INJURIES.get(team_name, [])

    if not injured:
        return 0

    # simple logic: boost if star teammate out
    return len(injured) * INJURY_BOOST


# --------------------------------------------------
# FINAL ROLE + INJURY ADJUSTMENT
# --------------------------------------------------

def role_adjustment(player, team=None):

    role_mult = role_boost(player)
    injury = injury_boost(player, team)

    return (role_mult - 1) * 10 + (injury * 10)