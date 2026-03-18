# --------------------------------------------------
# 🚀 ELITE API SERVER (STABLE PRODUCTION VERSION)
# --------------------------------------------------

from fastapi import FastAPI
import requests
import threading
import time
from datetime import datetime
import os

# SYSTEM IMPORTS
from bankroll_manager import get_bet_size, should_bet
from rl_agent import get_state, choose_action, update_q, get_reward, load_q
from alerts import send_discord_alert

# --------------------------------------------------
# INIT
# --------------------------------------------------

app = FastAPI()

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

if not ODDS_API_KEY:
    print("⚠️ WARNING: ODDS_API_KEY missing — odds disabled")

DAYS_AHEAD = 2
REFRESH_INTERVAL = 20

games_cache = {}
ALERTED = set()
BANKROLL = 1000

# ✅ NBA TEAM FILTER (NEW FIX)
NBA_TEAMS = {
    "atlanta hawks", "boston celtics", "brooklyn nets", "charlotte hornets",
    "chicago bulls", "cleveland cavaliers", "dallas mavericks", "denver nuggets",
    "detroit pistons", "golden state warriors", "houston rockets", "indiana pacers",
    "los angeles clippers", "los angeles lakers", "memphis grizzlies", "miami heat",
    "milwaukee bucks", "minnesota timberwolves", "new orleans pelicans",
    "new york knicks", "oklahoma city thunder", "orlando magic",
    "philadelphia 76ers", "phoenix suns", "portland trail blazers",
    "sacramento kings", "san antonio spurs", "toronto raptors",
    "utah jazz", "washington wizards"
}

# --------------------------------------------------
# UTILS
# --------------------------------------------------

def normalize(name):
    return name.lower().replace(" ", "").replace(".", "").replace("-", "")

def format_time(utc):
    try:
        dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return utc

# --------------------------------------------------
# 📅 SCHEDULE
# --------------------------------------------------

def get_schedule():
    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

    try:
        res = requests.get(url, timeout=5)  # ⚡ faster timeout
        data = res.json()

        out = {}

        for day in data["leagueSchedule"]["gameDates"][:DAYS_AHEAD]:
            date = day["gameDate"]
            games = {}

            for g in day.get("games", []):

                home = f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}"
                away = f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}"

                # ✅ FILTER NON-NBA TEAMS (FIXES MELBOURNE ISSUE)
                if home.lower() not in NBA_TEAMS or away.lower() not in NBA_TEAMS:
                    continue

                key = f"{normalize(away)}@{normalize(home)}"

                games[key] = {
                    "game_id": g["gameId"],
                    "home_team": home,
                    "away_team": away,
                    "time": format_time(g["gameTimeUTC"])
                }

            out[date] = games

        return out

    except Exception as e:
        print("❌ SCHEDULE ERROR:", e)
        return {}

# --------------------------------------------------
# 💰 ODDS
# --------------------------------------------------

def get_odds():
    if not ODDS_API_KEY:
        return []

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "totals"
    }

    try:
        res = requests.get(url, params=params, timeout=5)  # ⚡ faster timeout
        return res.json()
    except Exception as e:
        print("❌ ODDS ERROR:", e)
        return []

# --------------------------------------------------
# 🎯 ODDS MAP
# --------------------------------------------------

def build_odds_map(data):
    out = {}

    for g in data:
        try:
            home = normalize(g["home_team"])
            away = normalize(g["away_team"])

            total = None

            for book in g.get("bookmakers", []):
                for m in book.get("markets", []):
                    if m["key"] == "totals":
                        for o in m["outcomes"]:
                            if o["name"] == "Over":
                                total = o["point"]

            if total:
                out[f"{away}@{home}"] = total
                out[f"{home}@{away}"] = total

        except:
            continue

    return out

# --------------------------------------------------
# 🧠 MODEL
# --------------------------------------------------

def predict_total(game):
    base = 222
    pace_adj = (hash(game["game_id"]) % 10)
    noise = (hash(game["home_team"]) % 5)
    return base + pace_adj + noise

def calculate_edge(model, market):
    return round(model - market, 2)

def probability(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

def edge_score(edge):
    return abs(edge) * 10

# --------------------------------------------------
# 🔁 CORE ENGINE
# --------------------------------------------------

def build_games():
    schedule = get_schedule()
    odds = get_odds()
    odds_map = build_odds_map(odds)

    results = {}

    for date, games in schedule.items():
        results[date] = {}

        for key, g in games.items():

            market = odds_map.get(key)

            if not market:
                results[date][key] = {**g, "has_odds": False}
                continue

            model = predict_total(g)
            edge = calculate_edge(model, market)
            prob = probability(edge)
            score = edge_score(edge)

            state = get_state(edge, prob, 2)
            action = choose_action(state)

            bet = False
            bet_size = 0

            if action == "bet" and should_bet(score, prob, edge):

                bet = True

                bet_size = get_bet_size(
                    probability=prob,
                    edge_score=score,
                    bankroll=BANKROLL
                )

                if key not in ALERTED:
                    ALERTED.add(key)

                    send_discord_alert(f"""
🔥 AUTO BET

{g['away_team']} @ {g['home_team']}

Edge: {edge}
Prob: {round(prob,2)}
Score: {round(score,2)}

BET: {"OVER" if edge > 0 else "UNDER"} {market}
SIZE: ${bet_size}
""")

            results[date][key] = {
                **g,
                "market": market,
                "model": model,
                "edge": edge,
                "probability": round(prob, 3),
                "score": round(score, 2),
                "bet_size": bet_size,
                "auto_bet": bet
            }

    return results

# --------------------------------------------------
# 🔄 REFRESH LOOP (SAFE UPDATE)
# --------------------------------------------------

def refresh_loop():
    global games_cache

    while True:
        try:
            print("🔄 Updating...")

            new_data = build_games()  # compute first
            games_cache = new_data   # assign after

            print("✅ Updated")

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP (FAST + SAFE)
# --------------------------------------------------

@app.on_event("startup")
def startup():
    print("🚀 Starting system")

    try:
        load_q()
        print("✅ RL memory loaded")
    except Exception as e:
        print("❌ RL LOAD ERROR:", e)

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
    if not games_cache:
        return {"status": "loading"}
    return games_cache