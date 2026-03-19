# --------------------------------------------------
# 🚀 API SERVER (FULL SHARP SYSTEM + PRICE GAPS)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
from datetime import datetime
import random

# ---------------- IMPORTS ----------------

from prop_model import evaluate_prop
from odds_prop_scraper import get_odds_props
from bankroll_manager import get_bet_size
from clv_tracker import (
    record_prop_line,
    update_prop_line,
    calculate_clv,
    calculate_roi,
    model_health
)
from alerts import send_smart_alert
from prop_tracker import log_prop
from line_engine import group_lines, get_best_lines
from team_data import TEAM_STATS
from price_gap_engine import detect_price_gaps  # 🔥 NEW

# ---------------- INIT ----------------

app = FastAPI()

games_cache = {}
ALERTED = set()
REFRESH_INTERVAL = random.randint(40, 70)

# --------------------------------------------------
# 🔁 TEAM NORMALIZATION
# --------------------------------------------------

def normalize_team(name):

    if not name:
        return None

    name = name.replace("Los Angeles ", "")
    name = name.replace("LA ", "")

    replacements = {
        "Trail Blazers": "Blazers",
        "76ers": "Sixers",
        "NY Knicks": "Knicks",
        "GS Warriors": "Warriors"
    }

    for k, v in replacements.items():
        if k in name:
            name = v

    return name.strip()

def parse_teams(game):

    try:
        away, home = game.split("@")
        return away.strip(), home.strip()
    except:
        return None, None

# --------------------------------------------------
# 📈 LINE TRACKING
# --------------------------------------------------

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

# --------------------------------------------------
# 🔥 EDGE BOOST ENGINE
# --------------------------------------------------

def enhance_edge(edge, clv, movement, velocity):

    boost = 0

    if clv > 1:
        boost += 0.5
    if clv > 2:
        boost += 1

    if abs(movement) > 2:
        boost += 0.5

    if abs(velocity) > 0.05:
        boost += 0.5

    if (edge > 0 and movement > 0) or (edge < 0 and movement < 0):
        boost += 0.5

    if (edge > 0 and movement < 0) or (edge < 0 and movement > 0):
        boost -= 0.75

    return edge + boost

# --------------------------------------------------
# 🧠 GAME MODEL
# --------------------------------------------------

def evaluate_game_prop(game, line, market):

    away, home = parse_teams(game)

    away = normalize_team(away)
    home = normalize_team(home)

    if not away or not home:
        return None

    away_stats = TEAM_STATS.get(away)
    home_stats = TEAM_STATS.get(home)

    if not away_stats or not home_stats:
        return None

    if market == "total":

        pace = (away_stats["pace"] + home_stats["pace"]) / 2

        away_pts = pace * (away_stats["off"] / home_stats["def"])
        home_pts = pace * (home_stats["off"] / away_stats["def"])

        model_total = (away_pts + home_pts) / 2.2
        edge = model_total - line

    elif market == "spread":

        power_diff = (
            (home_stats["off"] - home_stats["def"])
            - (away_stats["off"] - away_stats["def"])
        )

        model_spread = power_diff / 2
        edge = model_spread - line

    else:
        return None

    prob = max(min(0.5 + edge / 12, 0.85), 0.45)

    return {
        "type": "game",
        "game": game,
        "market": market,
        "line": line,
        "edge": round(edge, 2),
        "probability": round(prob, 3),
        "bet": "OVER" if edge > 0 else "UNDER"
    }

# --------------------------------------------------
# 🔥 CORE ENGINE
# --------------------------------------------------

def build_props():

    # ---------------- FETCH ----------------
    raw = get_odds_props()

    # 🔥 GAP DETECTION (NEW)
    price_gaps = detect_price_gaps(raw)

    # ---------------- UNIFY ----------------
    grouped = group_lines(raw)
    raw = get_best_lines(grouped)

    player_props = []
    game_props = []

    for p in raw:

        if p.get("stat") in ["points", "rebounds", "assists"]:
            player_props.append(p)

        elif p.get("stat") in ["spread", "total"]:
            game_props.append(p)

    props_out = []

    # ---------------- PLAYER PIPELINE ----------------
    for p in player_props:

        try:
            result = evaluate_prop(
                player=p["player"],
                line=p["line"],
                stat=p["stat"]
            )

            if not result:
                continue

            edge = result["edge"]
            prob = result["probability"]

            # 🔥 GAP BOOST
            gap_boost = 0
            for g in price_gaps:
                if g["player"] == p["player"] and g["stat"] == p["stat"]:
                    gap_boost = g["confidence_boost"]
                    break

            edge += gap_boost

            key = f"{p['player']}-{p['stat']}"

            track_line(key, p["line"])
            movement, velocity = analyze_movement(key)

            record_prop_line(p["player"], p["stat"], p["line"])
            clv = update_prop_line(p["player"], p["stat"], p["line"])

            boosted = enhance_edge(edge, clv, movement, velocity)

            print(
                f"📈 {key} | {round(edge-gap_boost,2)} → {round(boosted,2)} "
                f"| GAP:+{gap_boost} | M:{movement} V:{velocity} CLV:{clv}"
            )

            if abs(boosted) < 0.4 or prob < 0.52:
                continue

            size = get_bet_size(
                probability=prob,
                edge_score=abs(boosted) * 10,
                bankroll=1000,
                clv=clv
            )

            result.update({
                "type": "player",
                "bet_size": size,
                "clv": clv,
                "edge": round(boosted, 2)
            })

            props_out.append(result)

        except Exception as e:
            print("❌ PLAYER ERROR:", e)

    # ---------------- GAME PIPELINE ----------------
    for p in game_props:

        try:
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

            print(
                f"📊 {key} | {edge} → {round(boosted,2)} "
                f"| M:{movement} V:{velocity}"
            )

            if abs(boosted) < 1.5 or prob < 0.52:
                continue

            size = get_bet_size(
                probability=prob,
                edge_score=abs(boosted) * 10,
                bankroll=1000
            )

            result["bet_size"] = size
            result["edge"] = round(boosted, 2)

            props_out.append(result)

        except Exception as e:
            print("❌ GAME ERROR:", e)

    # 🔥 OPTIONAL: expose gap signals
    props_out.extend(price_gaps)

    print(f"✅ TOTAL PLAYS: {len(props_out)}")
    return props_out

# --------------------------------------------------
# 🔄 LOOP
# --------------------------------------------------

def refresh_loop():

    global games_cache

    while True:
        try:
            print("\n🔄 SYSTEM UPDATE\n")

            games_cache = {
                "props": build_props(),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():
    print("🚀 SYSTEM STARTED (SHARP + GAP MODE)")
    threading.Thread(target=refresh_loop, daemon=True).start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

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
        "health": model_health(),
        "props_count": len(games_cache.get("props", []))
    }
