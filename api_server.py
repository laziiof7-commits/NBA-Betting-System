# --------------------------------------------------
# 🚀 ELITE API SERVER (HYBRID + CRASH-PROOF + ML READY)
# --------------------------------------------------

from fastapi import FastAPI
import requests
import threading
import time
from datetime import datetime
import os

# --------------------------------------------------
# SAFE IMPORTS (NEVER CRASH)
# --------------------------------------------------

try:
    from bankroll_manager import get_bet_size, should_bet
except:
    def get_bet_size(*args, **kwargs): return 0
    def should_bet(*args, **kwargs): return False

try:
    from rl_agent import load_q
except:
    def load_q(): print("⚠️ RL disabled")

try:
    from alerts import send_discord_alert
except:
    def send_discord_alert(msg): print("ALERT:", msg)

try:
    from lineup_model import lineup_adjustment
except:
    def lineup_adjustment(*args): return 0

try:
    from clv_tracker import log_bet
except:
    def log_bet(*args, **kwargs): pass

# PROP SYSTEM
try:
    from prizepicks_scraper import get_prizepicks_props
except:
    def get_prizepicks_props(): return []

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

# --------------------------------------------------
# INIT
# --------------------------------------------------

app = FastAPI()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")

REFRESH_INTERVAL = 20
games_cache = {}
ALERTED = set()
BANKROLL = 1000

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
# SCHEDULE
# --------------------------------------------------

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

# --------------------------------------------------
# ODDS
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
    except:
        return []

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

        except:
            continue

    return out

# --------------------------------------------------
# GAME MODEL
# --------------------------------------------------

def predict_total(game):

    base = 226
    base += lineup_adjustment(game["home_team"], game["away_team"])

    return round(base, 2)

def calc_edge(model, market):
    return round(model - market, 2)

def prob(edge):
    return max(min(0.5 + edge / 25, 0.75), 0.45)

def score(edge):
    return abs(edge) * 10

# --------------------------------------------------
# 🔥 FALLBACK PROP GENERATOR
# --------------------------------------------------

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

            if stat == "points":
                line = 25
            elif stat == "rebounds":
                line = 8
            elif stat == "assists":
                line = 7
            else:
                line = 10

            props.append({
                "player": player,
                "stat": stat,
                "line": line
            })

    print(f"⚠️ Using fallback props: {len(props)}")

    return props

# --------------------------------------------------
# 🔥 HYBRID PROP SYSTEM
# --------------------------------------------------

def build_props():

    props_out = []

    try:
        raw_props = get_prizepicks_props()

        # fallback trigger
        if not raw_props:
            print("⚠️ PrizePicks failed → fallback")
            raw_props = generate_fallback_props()

        for p in raw_props:

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

    except Exception as e:
        print("❌ PROP ERROR:", e)

    return props_out

# --------------------------------------------------
# CORE ENGINE
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
            edge = calc_edge(model, market)
            probability = prob(edge)
            edge_score = score(edge)

            bet = False
            bet_size = 0

            if (
                abs(edge) > 2
                and probability > 0.55
                and should_bet(edge_score, probability, edge)
            ):

                bet = True

                bet_size = get_bet_size(
                    probability=probability,
                    edge_score=edge_score,
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
🎯 Prob: {round(probability,2)}

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
                "probability": round(probability, 3),
                "bet_size": bet_size,
                "auto_bet": bet
            }

    results["props"] = build_props()

    return results

# --------------------------------------------------
# LOOP
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
    except:
        pass

    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()

# --------------------------------------------------
# API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}