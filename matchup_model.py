# --------------------------------------------------
# 🔥 MATCHUP + PACE MODEL (SHARP EDGE)
# --------------------------------------------------

# --------------------------------------------------
# TEAM PACE (POSSESSIONS PER GAME)
# --------------------------------------------------

TEAM_PACE = {
    "Pacers": 103,
    "Wizards": 102,
    "Hawks": 101,
    "Warriors": 101,
    "Lakers": 100,
    "Mavericks": 99,
    "Nuggets": 98,
    "Celtics": 97,
    "Knicks": 95
}

# default fallback
DEFAULT_PACE = 98


# --------------------------------------------------
# DEFENSE VS POSITION (SIMPLIFIED)
# lower = better defense
# higher = worse defense (good for props)
# --------------------------------------------------

DEFENSE = {
    "points": {
        "Hawks": 1.08,
        "Wizards": 1.10,
        "Spurs": 1.09,
        "Celtics": 0.92,
        "Knicks": 0.94
    },
    "rebounds": {
        "Pacers": 1.07,
        "Lakers": 1.05,
        "Celtics": 0.93
    },
    "assists": {
        "Hornets": 1.10,
        "Jazz": 1.08,
        "Knicks": 0.95
    }
}


# --------------------------------------------------
# GET TEAM NAME (SAFE CLEAN)
# --------------------------------------------------

def clean_team(team_name):

    if not team_name:
        return None

    return team_name.split()[-1]  # "Los Angeles Lakers" → "Lakers"


# --------------------------------------------------
# PACE ADJUSTMENT
# --------------------------------------------------

def pace_adjustment(team, opponent):

    t = clean_team(team)
    o = clean_team(opponent)

    pace_t = TEAM_PACE.get(t, DEFAULT_PACE)
    pace_o = TEAM_PACE.get(o, DEFAULT_PACE)

    avg = (pace_t + pace_o) / 2

    # normalize around league avg ~98
    return (avg - 98) * 0.15


# --------------------------------------------------
# DEFENSE ADJUSTMENT
# --------------------------------------------------

def defense_adjustment(stat, opponent):

    o = clean_team(opponent)

    if stat not in DEFENSE:
        return 0

    multiplier = DEFENSE[stat].get(o, 1.0)

    # convert multiplier into additive boost
    return (multiplier - 1) * 8


# --------------------------------------------------
# FINAL MATCHUP BOOST
# --------------------------------------------------

def matchup_boost(player, stat, team=None, opponent=None):

    boost = 0

    if team and opponent:
        boost += pace_adjustment(team, opponent)
        boost += defense_adjustment(stat, opponent)

    return round(boost, 2)