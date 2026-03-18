PLAYER_USAGE = {
    "LeBron James": 0.30,
    "Stephen Curry": 0.32,
    "Luka Doncic": 0.36,
    "Nikola Jokic": 0.31
}


def project_usage(player):

    return PLAYER_USAGE.get(player, 0.22)