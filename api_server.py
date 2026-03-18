# --------------------------------------------------
# 🚀 ELITE API SERVER (MULTI-SOURCE + STABLE)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
from datetime import datetime
import os
import random

# ---------------- SAFE IMPORT ----------------

def safe_import(module):
    try:
        return __import__(module, fromlist=["*"])
    except:
        return None

alerts = safe_import("alerts")
prop_model = safe_import("prop_model")
prop_tracker = safe_import("prop_tracker")
lineup_model = safe_import("lineup_model")
dk_scraper = safe_import("draftkings_scraper")
pp_scraper = safe_import("prizepicks_scraper")

# ---------------- SAFE FUNCTIONS ----------------

def send_alert(msg):
    try:
        if alerts and hasattr(alerts, "send_discord_alert"):
            alerts.send_discord_alert(msg)
        else:
            print(msg)
    except Exception as e:
        print("❌ Discord error:", e)

def evaluate_prop_safe(**kwargs):
    if prop_model:
        return prop_model.evaluate_prop(**kwargs)
    return None

def is_good_prop_safe(p):
    if prop_model:
        return prop_model.is_good_prop(p)
    return False

def bet_size_safe(p):
    if prop_model:
        return prop_model.prop_bet_size(p, base_size=10)
    return 0

def log_prop_safe(p):
    if prop_tracker:
        prop_tracker.log_prop(p)

def get_summary_safe():
    if prop_tracker:
        return prop_tracker.summary()
    return {
        "hit_rate": 0,
        "recent_hit_rate": 0,
        "roi": {"roi": 0, "profit": 0},
        "avg_clv": 0
    }

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = 45
games_cache = {}
ALERTED = set()
LAST_LINES = {}

# ---------------- FALLBACK ----------------

def generate_fallback_props():

    players = ["LeBron James", "Stephen Curry", "Luka Doncic", "Nikola Jokic"]
    stats = ["points", "rebounds", "assists"]

    props = []

    for player in players:
        for stat in stats:

            base = {
                "points": random.randint(24, 32),
                "rebounds": random.randint(7, 12),
                "assists": random.randint(6, 10)
            }

            props.append({
                "player": player,
                "stat": stat,
                "line": base[stat]
            })

    print(f"⚠️ FALLBACK props: {len(props)}")
    return props

# ---------------- MULTI-SOURCE FETCH ----------------

def get_props():

    # 🥇 DraftKings
    try:
        if dk_scraper and hasattr(dk_scraper, "get_dk_props"):
            props = dk_scraper.get_dk_props()
            if props:
                print(f"🔥 DRAFTKINGS: {len(props)} props")
                return props
    except Exception as e:
        print("❌ DK ERROR:", e)

    # 🟡 PrizePicks
    try:
        if pp_scraper and hasattr(pp_scraper, "get_prizepicks_props"):
            props = pp_scraper.get_prizepicks_props()
            if props:
                print(f"🟡 PRIZEPICKS: {len(props)} props")
                return props
    except Exception as e:
        print("❌ PP ERROR:", e)

    # 🔴 Fallback
    print("🚨 USING FALLBACK")
    return generate_fallback_props()

# ---------------- BUILD PROPS ----------------

def build_props():

    props_out = []
    raw_props = get_props()

    for p in raw_props:

        try:
            result = evaluate_prop_safe(
                player=p["player"],
                line=p["line"],
                stat=p["stat"]
            )

            if not result:
                continue

            # 🔍 DEBUG
            if abs(result["edge"]) > 1:
                print(f"📊 {result['player']} {result['stat']} | Edge: {result['edge']}")

            # ---------------- LINE MOVEMENT ----------------
            key = f"{p['player']}-{p['stat']}"
            prev = LAST_LINES.get(key)
            movement = (p["line"] - prev) if prev else 0

            LAST_LINES[key] = p["line"]
            result["movement"] = round(movement, 2)

            # ---------------- FILTER (FIXED) ----------------
            if abs(result["edge"]) > 1.5 and result["probability"] > 0.52:

                size = bet_size_safe(result)
                result["bet_size"] = size

                alert_key = f"{key}-{p['line']}"

                if alert_key not in ALERTED:

                    ALERTED.add(alert_key)
                    log_prop_safe(result)

                    send_alert(
                        f"🔥 {result['player']} {result['stat']} {result['bet']} "
                        f"| Edge: {result['edge']} | Size: ${size}"
                    )

                props_out.append(result)

        except Exception as e:
            print("❌ PROP ERROR:", e)

    print(f"✅ GOOD PROPS: {len(props_out)}")
    return props_out

# ---------------- LOOP ----------------

def refresh_loop():

    global games_cache

    while True:
        try:
            print("\n🔄 SYSTEM UPDATE\n")
            games_cache = {
                "props": build_props()
            }
        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# ---------------- START ----------------

@app.on_event("startup")
def startup():
    print("🚀 SYSTEM STARTED (MULTI-SOURCE MODE)")
    threading.Thread(target=refresh_loop, daemon=True).start()

# ---------------- API ----------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/props")
def props():
    return games_cache or {"status": "loading"}

# ---------------- DASHBOARD ----------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    stats = get_summary_safe()

    return f"""
    <html>
    <body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:40px;">
        <h1>🔥 Betting Dashboard</h1>
        <h2>ROI: {stats['roi']['roi']}%</h2>
        <h2>Profit: ${stats['roi']['profit']}</h2>
        <h2>Hit Rate: {stats['hit_rate']}</h2>
        <h2>Recent: {stats['recent_hit_rate']}</h2>
        <h2>Avg CLV: {stats['avg_clv']}</h2>
    </body>
    </html>
    """
