# --------------------------------------------------
# 🚀 ELITE API SERVER (FULLY INTEGRATED SYSTEM)
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

# 🔥 NEW PROP SYSTEM
from prop_scraper import get_player_props
from prop_model import evaluate_prop, is_good_prop, prop_bet_size
from prop_tracker import log_prop

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
# NBA TEAMS
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
        return requests.get(url, params=params, timeout=5).json()
    except:
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

            for book in g.get("bookmakers", []):
                for m in book.get("markets", []):
                    if m["key"] == "totals":
                        for o in m["outcomes"]:
                            if o["name"] == "Over":
                                out[f"{away}@{home}"] = o["point"]

        except:
            continue

    return out

# --------------------------------------------------
# 🧠 GAME MODEL
# --------------------------------------------------

def predict_total(game):

    base = 226

    model = base + (hash(game["home_team"]) % 6) - (hash(game["away_team"]) % 6)

    model += lineup_adjustment(game["home_team"], game["away_team"])

    return round(model, 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

def score(edge):
    return abs(edge) * 10

# --------------------------------------------------
# 🔥 PROP ENGINE
# --------------------------------------------------

def build_props():

    raw_props = get_player_props()
    final_props = []

    for p in raw_props:

        player = p["player"]
        stat = p["stat"]
        line = p["line"]

        prop = evaluate_prop(player, line, stat)

        if not prop:
            continue

        if is_good_prop(prop):

            stake = prop_bet_size(prop, 1)

            prop["stake"] = stake

            log_prop(prop)

            alert_key = f"{player}-{stat}-{line}"

            if alert_key not in ALERTED:
                ALERTED.add(alert_key)

                send_discord_alert(f"""
🔥 PROP BET

👤 {player}
📊 {stat.upper()} {line}

Edge: {prop['edge']}
Prob: {prop['probability']}
Conf: {prop['confidence']}

BET: {prop['bet']}
""")

        final_props.append(prop)

    return final_props

# --------------------------------------------------
# 🔁 CORE ENGINE
# --------------------------------------------------

def build_games():

    schedule = get_schedule()
    odds_map = build_odds_map(get_odds())

    results = {}

    for date, games in schedule.items():

        results[date] = {}

        for key, g in games.items():

            market = odds_map.get(key)

            if not market:
                results[date][key] = {**g, "has_odds": False}
                continue

            model = predict_total(g)
            edge = calc_edge(model, market)
            probability = prob(edge)
            edge_score = score(edge)

            state = get_state(edge, probability, 2)
            action = choose_action(state)

            bet = False
            bet_size = 0

            if action == "bet" and should_bet(edge_score, probability, edge):

                bet = True

                bet_size = get_bet_size(probability, edge_score, BANKROLL)

                alert_key = f"{key}-{market}"

                if alert_key not in ALERTED:
                    ALERTED.add(alert_key)

                    log_bet(
                        game=f"{g['away_team']}@{g['home_team']}",
                        bet_type="OVER" if edge > 0 else "UNDER",
                        line=market,
                        stake=bet_size,
                        model_line=model
                    )

                    send_discord_alert(f"🔥 GAME BET {g['away_team']} @ {g['home_team']}")

            results[date][key] = {
                **g,
                "market_total": market,
                "model_total": model,
                "edge": edge,
                "probability": probability,
                "edge_score": edge_score,
                "bet_size": bet_size,
                "auto_bet": bet
            }

    # 🔥 ADD PROPS
    results["props"] = build_props()

    return results

# --------------------------------------------------
# 🔄 REFRESH LOOP
# --------------------------------------------------

def refresh():

    global games_cache

    while True:

        try:
            print("🔄 Updating...")
            games_cache = build_games()
            print("✅ Updated")

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
        print("✅ RL Loaded")
    except:
        pass

    threading.Thread(target=refresh, daemon=True).start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}