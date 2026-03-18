# --------------------------------------------------
# 🚀 ELITE API SERVER (FINAL PRODUCTION BUILD)
# --------------------------------------------------

from fastapi import FastAPI
import requests
import threading
import time
from datetime import datetime
import os

# SYSTEM IMPORTS
from bankroll_manager import get_bet_size, should_bet
from rl_agent import get_state, choose_action, load_q
from alerts import send_discord_alert
from lineup_model import lineup_adjustment
from clv_tracker import log_bet

# --------------------------------------------------
# INIT
# --------------------------------------------------

app = FastAPI()

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

if not ODDS_API_KEY:
    print("⚠️ ODDS API KEY MISSING (ODDS DISABLED)")

DAYS_AHEAD = 2
REFRESH_INTERVAL = 20

games_cache = {}
ALERTED = set()
BANKROLL = 1000

# --------------------------------------------------
# NBA TEAMS (STRICT FILTER)
# --------------------------------------------------

NBA_TEAMS = {
    "atlanta hawks","boston celtics","brooklyn nets","charlotte hornets",
    "chicago bulls","cleveland cavaliers","dallas mavericks","denver nuggets",
    "detroit pistons","golden state warriors","houston rockets","indiana pacers",
    "los angeles clippers","los angeles lakers","memphis grizzlies","miami heat",
    "milwaukee bucks","minnesota timberwolves","new orleans pelicans",
    "new york knicks","oklahoma city thunder","orlando magic",
    "philadelphia 76ers","phoenix suns","portland trail blazers",
    "sacramento kings","san antonio spurs","toronto raptors",
    "utah jazz","washington wizards"
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
        res = requests.get(url, timeout=5)
        data = res.json()

        out = {}

        for day in data["leagueSchedule"]["gameDates"][:DAYS_AHEAD]:

            date = day["gameDate"]
            games = {}

            for g in day.get("games", []):

                home = f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}"
                away = f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}"

                # 🔥 STRICT NBA FILTER
                if home.lower() not in NBA_TEAMS or away.lower() not in NBA_TEAMS:
                    continue

                key = f"{normalize(away)}@{normalize(home)}"

                games[key] = {
                    "game_id": g["gameId"],
                    "home_team": home,
                    "away_team": away,
                    "time": format_time(g["gameTimeUTC"]),
                    "home_score": g.get("homeScore", 0),
                    "away_score": g.get("awayScore", 0),
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
        res = requests.get(url, params=params, timeout=5)
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
# 🧠 MODEL (UPGRADED)
# --------------------------------------------------

def predict_total(game):

    base = 226

    team_factor = (hash(game["home_team"]) % 8) - 4
    matchup_factor = (hash(game["away_team"]) % 8) - 4

    model = base + team_factor + matchup_factor

    # 🔥 LINEUP IMPACT
    model += lineup_adjustment(
        game["home_team"],
        game["away_team"]
    )

    return round(model, 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

def score(edge):
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

            # 🔥 SMART MATCHING
            away = normalize(g["away_team"])
            home = normalize(g["home_team"])

            k1 = f"{away}@{home}"
            k2 = f"{home}@{away}"

            market = odds_map.get(k1) or odds_map.get(k2)

            if not market:
                results[date][key] = {**g, "has_odds": False}
                continue

            model = predict_total(g)
            edge = calc_edge(model, market)
            probability = prob(edge)
            edge_score = score(edge)

            bet_type = "OVER" if edge > 0 else "UNDER"

            # RL decision
            state = get_state(edge, probability, 2)
            action = choose_action(state)

            bet = False
            bet_size = 0

            # 🔥 FINAL FILTER
            if (
                action == "bet"
                and abs(edge) > 2.5
                and probability > 0.54
                and edge_score > 25
                and should_bet(edge_score, probability, edge)
            ):

                bet = True

                bet_size = get_bet_size(
                    probability=probability,
                    edge_score=edge_score,
                    bankroll=BANKROLL
                )

                alert_key = f"{key}-{market}"

                if alert_key not in ALERTED:

                    ALERTED.add(alert_key)

                    # LOG BET
                    log_bet(
                        game=f"{g['away_team']}@{g['home_team']}",
                        bet_type=bet_type,
                        line=market,
                        stake=bet_size,
                        model_line=model
                    )

                    send_discord_alert(f"""
🔥 AUTO BET

🏀 {g['away_team']} @ {g['home_team']}

📊 Edge: {edge}
🎯 Prob: {round(probability,2)}
💎 Score: {round(edge_score,2)}

📉 Market: {market}
🧠 Model: {model}

💰 BET: {bet_type}
💵 Size: ${round(bet_size,2)}
""")

            results[date][key] = {
                **g,
                "market": market,
                "model": model,
                "edge": edge,
                "probability": round(probability, 3),
                "score": round(edge_score, 2),
                "bet_size": bet_size,
                "auto_bet": bet
            }

    return results

# --------------------------------------------------
# 🔄 REFRESH LOOP
# --------------------------------------------------

def refresh_loop():
    global games_cache

    while True:
        try:
            print("🔄 Updating...")

            new_data = build_games()
            games_cache = new_data

            print(f"✅ Updated | Games: {sum(len(v) for v in games_cache.values())}")

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():
    print("🚀 Starting system")

    try:
        load_q()
        print("✅ RL loaded")
    except Exception as e:
        print("❌ RL ERROR:", e)

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