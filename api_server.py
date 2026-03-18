# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

from fastapi import FastAPI
import requests
import threading
import time
from datetime import datetime
import os

from bankroll_manager import should_bet, get_adjusted_bet_size
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
    raise ValueError("❌ ODDS_API_KEY is missing")

DAYS_AHEAD = 3
REFRESH_INTERVAL = 15

games_cache = {}
ALERTED_GAMES = set()

# --------------------------------------------------
# TEAM NORMALIZATION
# --------------------------------------------------

def normalize(name):
    return (
        name.lower()
        .replace(" ", "")
        .replace(".", "")
        .replace("-", "")
        .replace("'", "")
    )

# --------------------------------------------------
# TIME FORMAT
# --------------------------------------------------

def format_time(utc):
    try:
        dt = datetime.fromisoformat(utc.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return utc

# --------------------------------------------------
# 📅 SCHEDULE
# --------------------------------------------------

def get_schedule(days_ahead=3):

    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        out = {}
        count = 0

        for day in data["leagueSchedule"]["gameDates"]:

            games = day.get("games", [])
            if not games:
                continue

            game_date = day["gameDate"]
            day_games = {}

            for g in games:

                try:
                    home = f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}"
                    away = f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}"

                    key = f"{normalize(away)}@{normalize(home)}"

                    day_games[key] = {
                        "game_id": g["gameId"],
                        "status": g["gameStatusText"],
                        "away_score": g.get("awayScore", 0),
                        "home_score": g.get("homeScore", 0),
                        "time": format_time(g["gameTimeUTC"]),
                        "home_team": home,
                        "away_team": away
                    }

                except Exception as e:
                    print("SCHEDULE ERROR:", e)

            if day_games:
                out[game_date] = day_games
                count += 1

            if count >= days_ahead:
                break

        return out

    except Exception as e:
        print("SCHEDULE FETCH ERROR:", e)
        return {}

# --------------------------------------------------
# 💰 ODDS FETCH
# --------------------------------------------------

def get_odds():

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "totals"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        print(f"📊 ODDS FETCHED: {len(data)} games")

        return data

    except Exception as e:
        print("ODDS ERROR:", e)
        return []

# --------------------------------------------------
# 🎯 ODDS MATCHING (UPGRADED)
# --------------------------------------------------

def build_odds_map(data):

    odds_map = {}

    for game in data:

        try:
            home_raw = game["home_team"]
            away_raw = game["away_team"]

            home = normalize(home_raw)
            away = normalize(away_raw)

            print(f"ODDS GAME: {away_raw} @ {home_raw}")

            total = None

            for book in game.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market["key"] == "totals":
                        for o in market["outcomes"]:
                            if o["name"] == "Over":
                                total = o["point"]

            if total:
                key1 = f"{away}@{home}"
                key2 = f"{home}@{away}"

                odds_map[key1] = total
                odds_map[key2] = total

                print(f"✅ MATCHED: {key1} → {total}")

        except Exception as e:
            print("ODDS MAP ERROR:", e)

    print(f"🎯 TOTAL ODDS MATCHED: {len(odds_map)}")

    return odds_map

# --------------------------------------------------
# 🧠 MODEL
# --------------------------------------------------

def predict_total(game):
    return 228 + (hash(game["game_id"]) % 12)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return round(min(max(0.5 + edge / 20, 0), 1), 3)

def score(edge):
    return round(abs(edge) * 2.5, 2)

# --------------------------------------------------
# 🔁 PIPELINE
# --------------------------------------------------

def build_games():

    schedule = get_schedule(DAYS_AHEAD)
    odds = get_odds()
    odds_map = build_odds_map(odds)

    final = {}

    for date, games in schedule.items():

        final[date] = {}

        for key, g in games.items():

            market = odds_map.get(key)

            has_odds = market is not None

            model = predict_total(g) if has_odds else None
            edge = calc_edge(model, market) if has_odds else None
            probability = prob(edge) if edge else None
            edge_score = score(edge) if edge else None

            bet_size = None
            is_bet = False

            if edge_score and probability:

                is_bet = should_bet(
                    edge_score=edge_score,
                    probability=probability,
                    clv_edge=edge
                )

                if is_bet:
                    bet_size = get_adjusted_bet_size(
                        probability=probability,
                        edge_score=edge_score,
                        bankroll=1000
                    )

                    if key not in ALERTED_GAMES:
                        ALERTED_GAMES.add(key)

                        send_discord_alert(f"""
🔥 NBA BET ALERT

{g['away_team']} @ {g['home_team']}

Edge: {edge}
Prob: {probability}
Score: {edge_score}

Bet: {"OVER" if edge > 0 else "UNDER"} {market}
Size: ${bet_size}
""")

            final[date][key] = {
                **g,
                "market_total": market,
                "has_odds": has_odds,
                "model_total": model,
                "edge": edge,
                "probability": probability,
                "edge_score": edge_score,
                "bet_size": bet_size,
                "auto_bet": is_bet
            }

    return final

# --------------------------------------------------
# 🔄 REFRESH LOOP
# --------------------------------------------------

def refresh():

    global games_cache

    while True:
        try:
            print("🔄 REFRESHING DATA...")
            games_cache = build_games()
            print("✅ UPDATED")
        except Exception as e:
            print("REFRESH ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():

    global games_cache

    print("🚀 INITIAL LOAD")
    games_cache = build_games()

    thread = threading.Thread(target=refresh, daemon=True)
    thread.start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def get_games():
    return games_cache