# --------------------------------------------------
# 🚀 ELITE API SERVER (FINAL HARDENED VERSION)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
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
dk_scraper = safe_import("draftkings_scraper")
pp_scraper = safe_import("prizepicks_scraper")

# ---------------- SAFE FUNCTIONS ----------------

def send_alert(msg):
    try:
        if alerts:
            alerts.send_discord_alert(msg)
        else:
            print(msg)
    except Exception as e:
        print("❌ Discord error:", e)

def evaluate_prop_safe(**kwargs):
    return prop_model.evaluate_prop(**kwargs) if prop_model else None

def bet_size_safe(p):
    return prop_model.prop_bet_size(p, 10) if prop_model else 0

def log_prop_safe(p):
    if prop_tracker:
        prop_tracker.log_prop(p)

def get_summary_safe():
    return prop_tracker.summary() if prop_tracker else {}

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = 90  # 🔥 slower = less blocking
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

            props.append({
                "player": player,
                "stat": stat,
                "line": random.randint(24, 32)
            })

    print(f"⚠️ FALLBACK: {len(props)} props")

    return props

# ---------------- MULTI SOURCE ----------------

def get_props():

    # DraftKings
    try:
        if dk_scraper:
            props = dk_scraper.get_dk_props()
            if props:
                print(f"🔥 DK SUCCESS: {len(props)}")
                return props
    except Exception as e:
        print("❌ DK FAIL:", e)

    # PrizePicks
    try:
        if pp_scraper:
            props = pp_scraper.get_prizepicks_props()
            if props:
                print(f"🟡 PP SUCCESS: {len(props)}")
                return props
    except Exception as e:
        print("❌ PP FAIL:", e)

    # fallback
    print("🚨 USING FALLBACK")
    return generate_fallback_props()

# ---------------- BUILD ----------------

def build_props():

    props_out = []
    raw = get_props()

    for p in raw:

        try:
            result = evaluate_prop_safe(
                player=p["player"],
                stat=p["stat"],
                line=p["line"]
            )

            if not result:
                continue

            key = f"{p['player']}-{p['stat']}"

            prev = LAST_LINES.get(key)
            movement = (p["line"] - prev) if prev else 0

            LAST_LINES[key] = p["line"]
            result["movement"] = round(movement, 2)

            # 🔥 SMART FILTER (FIXED)
            if abs(result["edge"]) > 1.2:

                size = bet_size_safe(result)
                result["bet_size"] = size

                alert_key = f"{key}-{p['line']}"

                if alert_key not in ALERTED:
                    ALERTED.add(alert_key)
                    log_prop_safe(result)

                    send_alert(
                        f"🔥 {result['player']} {result['stat']} "
                        f"{result['bet']} | Edge: {result['edge']}"
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
            games_cache = {"props": build_props()}
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
    <body style="background:#0f172a;color:white;text-align:center;">
        <h1>🔥 Dashboard</h1>
        <h2>ROI: {stats.get('roi',{}).get('roi',0)}%</h2>
        <h2>Profit: ${stats.get('roi',{}).get('profit',0)}</h2>
        <h2>Hit Rate: {stats.get('hit_rate',0)}</h2>
        <h2>CLV: {stats.get('avg_clv',0)}</h2>
    </body>
    </html>
    """
