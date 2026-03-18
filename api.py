from fastapi import FastAPI
from projection_engine import project_game
from monte_carlo import simulate_game
from edge_optimizer import edge_quality_score
from odds_api import get_live_odds
from nba_api import get_live_games

app = FastAPI()

@app.get("/games")
def get_games():

    odds = get_live_odds()
    live = get_live_games()

    results = []

    for game in odds:

        total = odds[game]

        proj = project_game(game, total)
        sim = simulate_game(proj, total)

        edge = proj["total"] - total
        prob = max(sim["over_probability"], sim["under_probability"])

        score = edge_quality_score(
            edge,
            prob,
            0,
            proj["confidence"],
            proj["matchup_volatility"]
        )

        results.append({
            "game": game,
            "market": total,
            "model": proj["total"],
            "edge": round(edge,2),
            "score": score
        })

    return results