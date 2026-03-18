# --------------------------------------------------
# 🚀 ELITE API SERVER (REAL + FALLBACK + STABLE)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
from datetime import datetime
import requests
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
odds_scraper = safe_import("odds_prop_scraper")

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
    stats = ["points"]

    props = []

    for player in players:
        for stat in stats:

            props.append({
                "player": player,
                "stat": stat,
                "line": random.randint(24, 32)
            })

    print(f"⚠️ Using fallback props: {len(props)}")
    return props

# ---------------- FETCH PROPS ----------------

def get_props():

    try:
        if odds_scraper and hasattr(odds_scraper, "get_odds_props"):

            props = odds_scraper.get_odds_props()

            if props:
                return props

    except Exception as e:
        print("❌ Odds API error:", e)

    print("🚨 USING FALLBACK (API FAILED)")
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

            print(f"📊 {result['player']} {result['stat']} | Edge: {result['edge']}")

            # ---------------- LINE MOVEMENT ----------------
            key = f"{p['player']}-{p['stat']}"
            prev = LAST_LINES.get(key)
            movement = (p["line"] - prev) if prev else 0

            LAST_LINES[key] = p["line"]
            result["movement"] = round(movement, 2)

            # ---------------- FILTER ----------------
            if abs(result["edge"]) > 1.5:

                size = bet_size_safe(result)
                result["bet_size"] = size

                alert_key = f"{key}-{p['line']}"

                if alert_key not in ALERTED:

                    ALERTED.add(alert_key)
                    log_prop_safe(result)

                    send_alert(
                        f"🔥 {result['player']} {result['stat']} "
                        f"{result['bet']} | Edge: {result['edge']} | Size: ${size}"
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
    print("🚀 SYSTEM STARTED")
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
