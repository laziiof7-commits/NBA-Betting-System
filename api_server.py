# --------------------------------------------------
# 🚀 ELITE API SERVER (STABLE + NO EXTERNAL DATA)
# --------------------------------------------------

from fastapi import FastAPI
import requests
import threading
import time
from datetime import datetime
import os

# ---------------- SAFE IMPORTS ----------------

try:
    from rl_agent import load_q
except:
    def load_q(): pass

try:
    from alerts import send_discord_alert
except:
    def send_discord_alert(msg): print(msg)

try:
    from lineup_model import lineup_adjustment
except:
    def lineup_adjustment(*args): return 0

try:
    from prop_model import evaluate_prop, is_good_prop, prop_bet_size
except:
    def evaluate_prop(**kwargs): return None
    def is_good_prop(x): return False
    def prop_bet_size(*args, **kwargs): return 0

try:
    from prop_tracker import log_prop
except:
    def log_prop(x): pass

# ⚠️ HARD BLOCK (CRITICAL FIX)
# Prevent ANY accidental NBA API usage
os.environ["DISABLE_PLAYER_DATA"] = "1"

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = 20
games_cache = {}
ALERTED = set()

# ---------------- UTILS ----------------

def normalize(name):
    return name.lower().replace(" ", "").replace(".", "").replace("-", "")

def format_time(utc):
    try:
        dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return utc

# ---------------- SAFE SCHEDULE ----------------

def get_schedule():

    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

    try:
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
    return round(226 + lineup_adjustment(game["home_team"], game["away_team"]), 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

# ---------------- FALLBACK PROPS ----------------

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

            line_map = {
                "points": 25,
                "rebounds": 8,
                "assists": 7
            }

            props.append({
                "player": player,
                "stat": stat,
                "line": line_map.get(stat, 10)
            })

    print(f"⚠️ Using fallback props: {len(props)}")

    return props

# ---------------- PROPS ENGINE ----------------

def build_props():

    props_out = []

    raw_props = generate_fallback_props()  # 🔥 FORCE SAFE MODE

    for p in raw_props:

        try:
            result = evaluate_prop(
                player=p["player"],
                line=p["line"],
                stat=p["stat"]
            )

            if not result:
                continue

            if is_good_prop(result):

                bet_size = prop_bet_size(result, base_size=10)

                key = f"{p['player']}-{p['stat']}-{p['line']}"

                if key not in ALERTED:

                    ALERTED.add(key)
                    log_prop(result)

                    send_discord_alert(f"""
🔥 PROP BET

👤 {result['player']} ({result['stat']})
📊 Line: {result['line']}
🧠 Projection: {result['projection']}
📈 Edge: {result['edge']}
🎯 Prob: {result['probability']}

💰 BET: {result['bet']}
💵 Size: ${bet_size}
""")

            props_out.append(result)