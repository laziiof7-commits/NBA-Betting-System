# --------------------------------------------------
# 📊 ODDS SCRAPER (PLAYER + GAME)
# --------------------------------------------------

from prizepicks_scraper import get_prizepicks_props

def get_odds_props():

    props = []

    # PLAYER PROPS
    try:
        pp = get_prizepicks_props()

        for p in pp:
            props.append({
                "player": p["player"],
                "stat": p["stat"],
                "line": p["line"]
            })

    except Exception as e:
        print("❌ PP ERROR:", e)

    # GAME PROPS (TEMP)
    game_lines = [
        {"game": "Lakers @ Heat", "stat": "total", "line": 228.5},
        {"game": "Lakers @ Heat", "stat": "spread", "line": -4.5},
        {"game": "Bucks @ Jazz", "stat": "total", "line": 221.5},
    ]

    props.extend(game_lines)

    return props
