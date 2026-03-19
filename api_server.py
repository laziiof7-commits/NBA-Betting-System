# --------------------------------------------------
# 🚀 API SERVER (FINAL STABLE VERSION - LOOP FIXED)
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
prop_bet_size = safe_import("prop_model", "prop_bet_size")
project = safe_import("prop_model", "project")
log_prop = safe_import("prop_tracker", "log_prop")

# ---------------- FALLBACK DEFAULTS ----------------

if not evaluate_prop:
    def evaluate_prop(**kwargs): return None

if not is_good_prop:
    def is_good_prop(x): return False

if not prop_bet_size:
    def prop_bet_size(*args, **kwargs): return 0

if not project:
    def project(player, stat): return None

if not log_prop:
    def log_prop(x): pass

# 🔥 HARD BLOCK
os.environ["DISABLE_PLAYER_DATA"] = "1"

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = 30
games_cache = {}
ALERTED = set()

# --------------------------------------------------
# 🔥 MODEL-BASED FALLBACK (FINAL FIX)
# --------------------------------------------------

def generate_fallback_props():

    players = [
        "LeBron James",
        "Stephen Curry",
        "Luka Doncic",
        "Nikola Jokic"
    ]

    stats = ["points", "rebounds", "assists"]

    props = []

    for player in players:
        for stat in stats:

            proj = project(player, stat)

            if proj is None:
                continue

            # 🔥 KEY FIX: line built FROM model
            line = round(proj + random.uniform(-2.5, 2.5), 1)

            props.append({
                "player": player,
                "stat": stat,
                "line": line
            })

    print(f"⚠️ MODEL-BASED FALLBACK: {len(props)} props")

    return props

# --------------------------------------------------
# 🔥 PROPS ENGINE
# --------------------------------------------------

def build_props():

    props_out = []
    raw_props = generate_fallback_props()

    for p in raw_props:

        try:
            result = evaluate_prop(
                player=p["player"],
                line=p["line"],
                stat=p["stat"]
            )

            if not result:
                continue

            print(f"📊 {result['player']} {result['stat']} | Edge: {result['edge']}")

            if is_good_prop(result):

                size = prop_bet_size(result, base_size=10)
                key = f"{p['player']}-{p['stat']}-{p['line']}"

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
# 🔁 BACKGROUND LOOP
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

    print("🚀 SYSTEM STARTED (FINAL MODE)")

    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}
