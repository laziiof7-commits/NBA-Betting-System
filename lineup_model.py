# --------------------------------------------------
# 🧠 LINEUP IMPACT ENGINE (PRO VERSION)
# --------------------------------------------------

# STAR IMPACT (when OUT → lowers team total)
LINEUP_IMPACT = {
    "Trae Young": -6,
    "Luka Doncic": -7,
    "Stephen Curry": -6,
    "Nikola Jokic": -6,
    "Kevin Durant": -6,
    "LeBron James": -5,
    "Joel Embiid": -7,
    "Giannis Antetokounmpo": -7
}

# ROLE PLAYER IMPACT (smaller effect)
ROLE_IMPACT = {
    "Austin Reaves": -2,
    "Klay Thompson": -3,
    "Jamal Murray": -3
}

# TEAM INJURIES (will be auto-updated later)
TEAM_INJURIES = {}


# --------------------------------------------------
# 🔥 MAIN TEAM ADJUSTMENT
# --------------------------------------------------

def lineup_adjustment(home_team, away_team):

    adjustment = 0

    home_injuries = TEAM_INJURIES.get(home_team, [])
    away_injuries = TEAM_INJURIES.get(away_team, [])

    # -------------------------
    # HOME TEAM
    # -------------------------
    for player in home_injuries:

        if player in LINEUP_IMPACT:
            adjustment += LINEUP_IMPACT[player]

        elif player in ROLE_IMPACT:
            adjustment += ROLE_IMPACT[player]

    # -------------------------
    # AWAY TEAM
    # -------------------------
    for player in away_injuries:

        if player in LINEUP_IMPACT:
            adjustment += LINEUP_IMPACT[player]

        elif player in ROLE_IMPACT:
            adjustment += ROLE_IMPACT[player]

    return adjustment


# --------------------------------------------------
# 🔥 PLAYER USAGE BOOST (FOR PROPS)
# --------------------------------------------------

def usage_boost(player, team):

    injuries = TEAM_INJURIES.get(team, [])

    boost = 0

    for injured in injuries:

        # star out → teammates benefit
        if injured in LINEUP_IMPACT and injured != player:
            boost += 2

    return boost


# --------------------------------------------------
# 🔥 INJURY INGESTION (AUTO UPDATE)
# --------------------------------------------------

def update_team_injuries(injury_data):

    """
    injury_data format:
    {
        "Los Angeles Lakers": ["LeBron James"],
        "Dallas Mavericks": ["Luka Doncic"]
    }
    """

    global TEAM_INJURIES

    TEAM_INJURIES = injury_data


# --------------------------------------------------
# 🔥 TEAM-LEVEL BREAKDOWN (DEBUG TOOL)
# --------------------------------------------------

def get_lineup_report(team):

    injuries = TEAM_INJURIES.get(team, [])

    report = []

    for player in injuries:

        impact = 0

        if player in LINEUP_IMPACT:
            impact = LINEUP_IMPACT[player]
        elif player in ROLE_IMPACT:
            impact = ROLE_IMPACT[player]

        report.append({
            "player": player,
            "impact": impact
        })

    return report