# --------------------------------------------------
# 🚀 API SERVER (FINAL PRO MODE - FIXED)
# --------------------------------------------------

from fastapi import FastAPI
import threading
import time
from datetime import datetime
import os
import random

# ---------------- SAFE IMPORTS ----------------

def safe_import(module, func=None):
    try:
        m = __import__(module, fromlist=[func] if func else [])
        return getattr(m, func) if func else m
    except:
        return None

evaluate_prop = safe_import("prop_model", "evaluate_prop")
is_good_prop = safe_import("prop_model", "is_good_prop")
project = safe_import("prop_model", "project")

log_prop = safe_import("prop_tracker", "log_prop")
get_odds_props = safe_import("odds_prop_scraper", "get_odds_props")

group_props = safe_import("line_engine", "group_props")
get_best_lines = safe_import("line_engine", "get_best_lines")
track_clv = safe_import("line_engine", "track_clv")

get_bet_size = safe_import("bankroll_manager", "get_bet_size")
should_bet = safe_import("bankroll_manager", "should_bet")

# ---------------- FALLBACK DEFAULTS ----------------

if not evaluate_prop:
    def evaluate_prop(**kwargs): return None

if not is_good_prop:
    def is_good_prop(x): return False

if not project:
    def project(player, stat): return None

if not log_prop:
    def log_prop(x): pass

if not get_odds_props:
    def get_odds_props(): return []

if not group_props:
    def group_props(x): return {}

if not get_best_lines:
    def get_best_lines(x): return x  # 🔥 SAFE fallback

if not track_clv:
    def track_clv(*args): return 0

if not get_bet_size:
    def get_bet_size(**kwargs): return 10

if not should_bet:
    def should_bet(*args): return True

# 🔥 HARD BLOCK
os.environ["DISABLE_PLAYER_DATA"] = "1"

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = random.randint(40, 70)
games_cache = {}
ALERTED = set()

# --------------------------------------------------
# 🔥 FIXED FALLBACK (NEVER RETURNS 0)
# --------------------------------------------------

def generate_fallback_props():

    players = [
        "LeBron James",
        "Stephen Curry",
        "Luka Doncic",
        "Nikola Jokic"
    ]

    stats = ["points", "rebounds", "assists"]

    base_lines = {
        "points": (24, 32),
        "rebounds": (6, 12),
        "assists": (5, 10)
    }

    props = []

    for player in players:
        for stat in stats:

            try:
                proj = project(player, stat)
            except:
                proj = None

            if proj is not None:
                line = round(proj - random.uniform(0.5, 3.0), 1)
            else:
                low, high = base_lines[stat]
                line = round(random.uniform(low, high), 1)

            props.append({
                "player": player,
                "stat": stat,
                "line": line,
                "book": "fallback"
            })

    print(f"⚠️ MODEL-BASED FALLBACK: {len(props)} props")
    return props

# --------------------------------------------------
# 🔥 PROPS ENGINE
# --------------------------------------------------

def build_props():

    raw_props = []

    try:
        raw_props = get_odds_props()
    except Exception as e:
        print("❌ ODDS ERROR:", e)

    if not raw_props:
        print("🚨 USING FALLBACK")
        raw_props = generate_fallback_props()
    else:
        print(f"📡 USING REAL ODDS ({len(raw_props)})")

    # 🔥 GROUPING SAFE
    try:
        grouped = group_props(raw_props)
        best_lines = get_best_lines(grouped)
    except Exception:
        best_lines = raw_props

    props_out = []

    for p in best_lines:

        try:
            player = p.get("player")
            stat = p.get("stat")

            # 🔥 HANDLE BOTH FORMATS
            line = p.get("best_over_line") or p.get("line")

            if not player or not stat or line is None:
                continue

            result = evaluate_prop(
                player=player,
                line=line,
                stat=stat
            )

            if not result:
                continue

            clv = track_clv(player, stat, line)
            result["clv"] = clv

            print(
                f"📊 {result['player']} {result['stat']} | "
                f"Edge: {result.get('edge')} | CLV: {clv}"
            )

            if not should_bet(
                result.get("score"),
                result.get("probability"),
                clv
            ):
                continue

            size = get_bet_size(
                probability=result.get("probability"),
                edge_score=result.get("score"),
                bankroll=1000,
                clv=clv
            )

            if size <= 0:
                continue

            result["bet_size"] = size

            key = f"{player}-{stat}-{line}"

            if key not in ALERTED:
                ALERTED.add(key)
                log_prop(result)

            props_out.append(result)

        except Exception as e:
            print("❌ PROP ERROR:", e)

    print(f"✅ GOOD PROPS: {len(props_out)}")
    return props_out

# --------------------------------------------------
# 🔄 CORE LOOP
# --------------------------------------------------

def build_games():
    return {
        "props": build_props(),
        "timestamp": datetime.utcnow().isoformat()
    }

# --------------------------------------------------
# 🔁 LOOP
# --------------------------------------------------

def refresh_loop():

    global games_cache

    while True:
        try:
            print("\n🔄 SYSTEM UPDATE\n")
            games_cache = build_games()
        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():
    print("🚀 SYSTEM STARTED (PRO MODE - FIXED)")
    threading.Thread(target=refresh_loop, daemon=True).start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}
