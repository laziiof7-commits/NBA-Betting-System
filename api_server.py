# --------------------------------------------------
# 🚀 API SERVER (FULL SHARP SYSTEM)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
from datetime import datetime
import random

# ---------------- IMPORTS ----------------

from prop_model import evaluate_prop, project
from odds_prop_scraper import get_odds_props
from bankroll_manager import get_bet_size
from clv_tracker import record_prop_line, update_prop_line, calculate_clv, calculate_roi, model_health
from alerts import send_smart_alert
from prop_tracker import log_prop

# ---------------- INIT ----------------

app = FastAPI()

games_cache = {}
ALERTED = set()
REFRESH_INTERVAL = random.randint(40, 70)

# ---------------- LINE MEMORY ----------------

LINE_HISTORY = {}

def track_line(key, line):
    if key not in LINE_HISTORY:
        LINE_HISTORY[key] = []

    LINE_HISTORY[key].append({
        "line": line,
        "time": time.time()
    })

    LINE_HISTORY[key] = LINE_HISTORY[key][-6:]

def analyze_movement(key):
    history = LINE_HISTORY.get(key, [])

    if len(history) < 2:
        return 0, 0

    start = history[0]["line"]
    end = history[-1]["line"]

    movement = end - start
    dt = history[-1]["time"] - history[0]["time"]
    velocity = movement / dt if dt > 0 else 0

    return round(movement, 2), round(velocity, 4)

# ---------------- EDGE BOOST ----------------

def enhance_edge(edge, clv, movement, velocity):

    boost = 0

    if clv > 1: boost += 0.5
    if clv > 2: boost += 1

    if abs(movement) > 2: boost += 0.5
    if abs(velocity) > 0.05: boost += 0.5

    if (edge > 0 and movement > 0): boost += 0.5
    if (edge < 0 and movement < 0): boost += 0.5

    if (edge > 0 and movement < 0): boost -= 0.75
    if (edge < 0 and movement > 0): boost -= 0.75

    return edge + boost

# ---------------- TEAM MODEL ----------------

TEAM_STATS = {
    "Lakers": {"pace": 101, "off": 114, "def": 113},
    "Warriors": {"pace": 102, "off": 116, "def": 115},
    "Celtics": {"pace": 99, "off": 118, "def": 110},
    "Nuggets": {"pace": 97, "off": 117, "def": 112},
    "Bucks": {"pace": 100, "off": 119, "def": 113},
    "Suns": {"pace": 98, "off": 115, "def": 114},
}

def parse_teams(game):
    try:
        a, b = game.split("@")
        return a.strip(), b.strip()
    except:
        return None, None

def evaluate_game_prop(game, line, market):

    away, home = parse_teams(game)

    if not away or not home:
        return None

    a = TEAM_STATS.get(away)
    h = TEAM_STATS.get(home)

    if not a or not h:
        return None

    if market == "total":
        pace = (a["pace"] + h["pace"]) / 2
        pts = (pace * (a["off"]/h["def"]) + pace * (h["off"]/a["def"])) / 2.2
        edge = pts - line
        model_line = pts

    elif market == "spread":
        diff = (h["off"]-h["def"]) - (a["off"]-a["def"])
        model_line = diff / 2
        edge = model_line - line

    else:
        return None

    prob = max(min(0.5 + edge/12, 0.85), 0.45)

    return {
        "type": "game",
        "game": game,
        "market": market,
        "line": line,
        "edge": round(edge, 2),
        "probability": round(prob, 3),
        "bet": "OVER" if edge > 0 else "UNDER"
    }

# ---------------- CORE ENGINE ----------------

def build_props():

    raw = get_odds_props()

    player_props = []
    game_props = []

    for p in raw:

        if p.get("stat") in ["points","rebounds","assists"]:
            player_props.append(p)

        elif p.get("stat") in ["spread","total"]:
            game_props.append(p)

    props_out = []

    # PLAYER
    for p in player_props:

        result = evaluate_prop(
            player=p["player"],
            line=p["line"],
            stat=p["stat"]
        )

        if not result:
            continue

        edge = result["edge"]
        prob = result["probability"]

        key = f"{p['player']}-{p['stat']}"

        track_line(key, p["line"])
        movement, velocity = analyze_movement(key)

        record_prop_line(p["player"], p["stat"], p["line"])
        clv = update_prop_line(p["player"], p["stat"], p["line"])

        boosted = enhance_edge(edge, clv, movement, velocity)

        if abs(boosted) < 0.2 or prob < 0.5:
            continue

        size = get_bet_size(
            probability=prob,
            edge_score=abs(boosted)*10,
            bankroll=1000,
            clv=clv
        )

        result.update({
            "type": "player",
            "bet_size": size,
            "clv": clv
        })

        props_out.append(result)

    # GAME
    for p in game_props:

        result = evaluate_game_prop(
            p.get("game"),
            p.get("line"),
            p.get("stat")
        )

        if not result:
            continue

        edge = result["edge"]
        prob = result["probability"]

        key = f"{p.get('game')}-{p.get('stat')}"

        track_line(key, p["line"])
        movement, velocity = analyze_movement(key)

        boosted = enhance_edge(edge, 0, movement, velocity)

        if abs(boosted) < 1.5 or prob < 0.52:
            continue

        size = get_bet_size(
            probability=prob,
            edge_score=abs(boosted)*10,
            bankroll=1000
        )

        result["bet_size"] = size

        props_out.append(result)

    print(f"✅ TOTAL PLAYS: {len(props_out)}")
    return props_out

# ---------------- LOOP ----------------

def refresh_loop():
    global games_cache
    while True:
        games_cache = {
            "props": build_props(),
            "timestamp": datetime.utcnow().isoformat()
        }
        time.sleep(REFRESH_INTERVAL)

@app.on_event("startup")
def start():
    threading.Thread(target=refresh_loop, daemon=True).start()

# ---------------- API ----------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/props")
def props():
    return games_cache.get("props", [])

@app.get("/dashboard")
def dashboard():
    return {
        "roi": calculate_roi(),
        "clv": calculate_clv(),
        "health": model_health()
    }
