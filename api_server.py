# --------------------------------------------------
# 🚀 ELITE API SERVER (STABLE + UPGRADED)
# --------------------------------------------------

from fastapi import FastAPI
import threading
import time
from datetime import datetime
import requests
import os
import random

# ---------------- SAFE IMPORTS ----------------

def safe_import(module):
    try:
        return __import__(module, fromlist=["*"])
    except Exception:
        return None

alerts = safe_import("alerts")
prop_model = safe_import("prop_model")
prop_tracker = safe_import("prop_tracker")
lineup_model = safe_import("lineup_model")
prizepicks = safe_import("prizepicks_scraper")
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
    if prop_model and hasattr(prop_model, "evaluate_prop"):
        return prop_model.evaluate_prop(**kwargs)
    return None

def is_good_prop_safe(prop):
    if prop_model and hasattr(prop_model, "is_good_prop"):
        return prop_model.is_good_prop(prop)
    return False

def bet_size_safe(prop):
    if prop_model and hasattr(prop_model, "prop_bet_size"):
        return prop_model.prop_bet_size(prop, base_size=10)
    return 0

def log_prop_safe(prop):
    if prop_tracker and hasattr(prop_tracker, "log_prop"):
        prop_tracker.log_prop(prop)

def lineup_adjustment_safe(team, opponent):
    if lineup_model and hasattr(lineup_model, "lineup_adjustment"):
        return lineup_model.lineup_adjustment(team, opponent)
    return 0

# 🔥 HARD BLOCK
os.environ["DISABLE_PLAYER_DATA"] = "1"

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = 45
games_cache = {}
ALERTED = set()
LAST_LINES = {}

# ---------------- UTILS ----------------

def normalize(name):
    return name.lower().replace(" ", "").replace(".", "").replace("-", "")

def format_time(utc):
    try:
        dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return utc

# ---------------- SCHEDULE ----------------

def get_schedule():
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        res = requests.get(url, timeout=5)
        data = res.json()

        out = {}

        for day in data["leagueSchedule"]["gameDates"][:2]:
            date = day["gameDate"]
            games = {}

            for g in day.get("games", []):
                home = f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}"
                away = f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}"

                key = f"{normalize(away)}@{normalize(home)}"

                games[key] = {
                    "home_team": home,
                    "away_team": away,
                    "time": format_time(g["gameTimeUTC"]),
                }

            out[date] = games

        return out

    except Exception as e:
        print("❌ SCHEDULE ERROR:", e)
        return {}

# ---------------- MODEL ----------------

def predict_total(game):
    return round(226 + lineup_adjustment_safe(game["home_team"], game["away_team"]), 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

# ---------------- PROP DATA PIPELINE ----------------

def get_props():
    # PrizePicks first
    try:
        if prizepicks and hasattr(prizepicks, "get_prizepicks_props"):
            props = prizepicks.get_prizepicks_props()
            if props:
                print(f"🔥 PrizePicks props: {len(props)}")
                return props
    except Exception as e:
        print("❌ PrizePicks error:", e)

    # Odds API second
    try:
        if odds_scraper and hasattr(odds_scraper, "get_odds_props"):
            props = odds_scraper.get_odds_props()
            if props:
                print(f"📊 Odds API props: {len(props)}")
                return props
    except Exception as e:
        print("❌ Odds API error:", e)

    return []

# --------------------------------------------------
# 🔥 MODEL-BASED FALLBACK
# --------------------------------------------------

def generate_fallback_props():
    players = [
        "LeBron James",
        "Stephen Curry",
        "Luka Doncic",
        "Nikola Jokic",
    ]

    props = []

    for player in players:
        for stat in ["points", "rebounds", "assists"]:
            base = evaluate_prop_safe(
                player=player,
                line=0,
                stat=stat
            )

            if not base:
                continue

            projection = base["projection"]
            line = round(projection + random.uniform(-2.5, 2.5), 1)

            props.append({
                "player": player,
                "stat": stat,
                "line": line
            })

    # intentionally muted to reduce spam
    # print(f"⚠️ Using MODEL fallback props: {len(props)}")

    return props

# --------------------------------------------------
# 🔥 BUILD PROPS
# --------------------------------------------------

def build_props():
    props_out = []

    raw_props = get_props()

    if not raw_props or len(raw_props) < 5:
        print("🚨 Using MODEL fallback")
        raw_props = generate_fallback_props()

    for p in raw_props:
        try:
            result = evaluate_prop_safe(
                player=p["player"],
                line=p["line"],
                stat=p["stat"]
            )

            if not result:
                continue

            # reduce log spam
            if abs(result["edge"]) > 1.5:
                print(f"📊 {result['player']} {result['stat']} | Edge: {result['edge']}")

            key = f"{p['player']}-{p['stat']}"
            prev = LAST_LINES.get(key)
            movement = (p["line"] - prev) if prev is not None else 0

            LAST_LINES[key] = p["line"]
            result["movement"] = round(movement, 2)

            if is_good_prop_safe(result):
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

# ---------------- CORE ----------------

def build_games():
    schedule = get_schedule()
    results = {}

    for date, games in schedule.items():
        results[date] = {}

        for key, g in games.items():
            model = predict_total(g)
            market = 226
            edge = calc_edge(model, market)

            results[date][key] = {
                **g,
                "market": market,
                "model": model,
                "edge": edge,
                "probability": prob(edge)
            }

    results["props"] = build_props()
    return results

# ---------------- LOOP ----------------

def refresh_loop():
    global games_cache

    while True:
        try:
            print("\n🔄 SYSTEM UPDATE\n")
            games_cache = build_games()
        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# ---------------- STARTUP ----------------

@app.on_event("startup")
def startup():
    print("🚀 SYSTEM STARTED")
    threading.Thread(target=refresh_loop, daemon=True).start()

# ---------------- API ----------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}
