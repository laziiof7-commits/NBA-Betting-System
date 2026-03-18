PLAYER_MINUTES = {
    "LeBron James": 35,
    "Stephen Curry": 34,
    "Luka Doncic": 36,
    "Nikola Jokic": 35
}


def project_minutes(player, game_context=None):

    base = PLAYER_MINUTES.get(player, 30)

    # simple adjustments
    if game_context == "blowout":
        base -= 4

    return base