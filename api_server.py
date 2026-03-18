# --------------------------------------------------
# 🚀 ELITE API SERVER (STABLE + LIVE PROPS + NO FAILS)
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

# 🔥 PROP SYSTEM
from prizepicks_scraper import get_prizepicks_props
from prop_model import evaluate_prop, is_good_prop, prop_bet_size
from prop_tracker import log_prop

app = FastAPI()

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

REFRESH_INTERVAL = 20
BANKROLL = 1000

games_cache = {}
ALERTED = set()

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

    try:
        res = requests.get(
            "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json",
            timeout=5
        )

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
                    "game_id": g["gameId"],
                    "home_team": home,
                    "away_team": away,
                    "time": format_time(g["gameTimeUTC"]),
                }

            out[date] = games

        return out

    except Exception as e:
        print("❌ SCHEDULE ERROR:", e)
        return {}

# --------------------------------------------------
# 💰 ODDS (SAFE)
# --------------------------------------------------

def get_odds():

    if not ODDS_API_KEY:
        return {}

    try:
        res = requests.get(
            "https://api.the-odds-api.com/v4/sports/basketball_nba/odds",
            params={
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "totals"
            },
            timeout=5
        )

        return res.json()

    except Exception as e:
        print("❌ ODDS ERROR:", e)
        return {}

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
    return round(base + lineup_adjustment(game["home_team"], game["away_team"]), 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

def score(edge):
    return abs(edge) * 10

# --------------------------------------------------
# 🔥 PROPS ENGINE (FIXED + SAFE)
# --------------------------------------------------

def build_props():

    try:
        raw_props = get_prizepicks_props()

        if not raw_props:
            print("⚠️ No props returned")
            return []

        results = []

        for p in raw_props:

            try:
                result = evaluate_prop(
                    player=p["player"],
                    line=p["line"],
                    stat=p["stat"]
                )

                if not result:
                    continue

                results.append(result)

                # 🔥 BET FILTER
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

            except Exception as e:
                print("⚠️ PROP SKIP:", e)

        return results

    except Exception as e:
        print("❌ PROP ENGINE ERROR:", e)
        return []

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

            p = prob(edge)
            s = score(edge)

            bet = False
            bet_size = 0

            if (
                abs(edge) > 2
                and p > 0.55
                and s > 20
                and should_bet(s, p, edge)
            ):

                bet = True

                bet_size = get_bet_size(
                    probability=p,
                    edge_score=s,
                    bankroll=BANKROLL
                )

                if key not in ALERTED:

                    ALERTED.add(key)

                    log_bet(
                        game=f"{g['away_team']}@{g['home_team']}",
                        bet_type="OVER" if edge > 0 else "UNDER",
                        line=market,
                        stake=bet_size,
                        model_line=model
                    )

                    send_discord_alert(f"""
🔥 GAME BET

🏀 {g['away_team']} @ {g['home_team']}
📊 Edge: {edge}
🎯 Prob: {round(p,2)}
💎 Score: {round(s,2)}

📉 Market: {market}
🧠 Model: {model}

💰 BET: {"OVER" if edge > 0 else "UNDER"}
💵 Size: ${round(bet_size,2)}
""")

            results[date][key] = {
                **g,
                "market": market,
                "model": model,
                "edge": edge,
                "probability": round(p, 3),
                "score": round(s, 2),
                "bet_size": bet_size,
                "auto_bet": bet
            }

    results["props"] = build_props()

    return results

# --------------------------------------------------
# 🔄 LOOP
# --------------------------------------------------

def refresh_loop():

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
# STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():

    print("🚀 Starting system")

    try:
        load_q()
        print("✅ RL Loaded")
    except:
        pass

    threading.Thread(target=refresh_loop, daemon=True).start()

# --------------------------------------------------
# API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache if games_cache else {"status": "loading"}