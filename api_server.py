# --------------------------------------------------
# 🚀 API SERVER (PRO MODE - HYBRID + FINAL)
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import threading
import time
from datetime import datetime
import os
import random

# ---------------- SAFE IMPORTS ----------------

def safe_import(module, func=None):
    try:
        m = __import__(module, fromlist=[func] if func else [])
        return getattr(m, func) if func else m
    except:
        return None

evaluate_prop = safe_import("prop_model", "evaluate_prop")
project = safe_import("prop_model", "project")

log_prop = safe_import("prop_tracker", "log_prop")
get_odds_props = safe_import("odds_prop_scraper", "get_odds_props")

group_props = safe_import("line_engine", "group_props")
get_best_lines = safe_import("line_engine", "get_best_lines")

get_bet_size = safe_import("bankroll_manager", "get_bet_size")

record_prop_line = safe_import("clv_tracker", "record_prop_line")
update_prop_line = safe_import("clv_tracker", "update_prop_line")

calculate_clv = safe_import("clv_tracker", "calculate_clv")
calculate_roi = safe_import("clv_tracker", "calculate_roi")
model_health = safe_import("clv_tracker", "model_health")

send_smart_alert = safe_import("alerts", "send_smart_alert")

# ---------------- FALLBACK DEFAULTS ----------------

if not evaluate_prop:
    def evaluate_prop(**kwargs): return None

if not project:
    def project(player, stat): return None

if not log_prop:
    def log_prop(x): pass

if not get_odds_props:
    def get_odds_props(): return []

if not group_props:
    def group_props(x): return {}

if not get_best_lines:
    def get_best_lines(x): return x

if not get_bet_size:
    def get_bet_size(**kwargs): return 10

if not record_prop_line:
    def record_prop_line(*args): pass

if not update_prop_line:
    def update_prop_line(*args): return 0

if not send_smart_alert:
    def send_smart_alert(*args): pass

# 🔥 HARD BLOCK
os.environ["DISABLE_PLAYER_DATA"] = "1"

# ---------------- INIT ----------------

app = FastAPI()

REFRESH_INTERVAL = random.randint(40, 70)
games_cache = {}
ALERTED = set()

# --------------------------------------------------
# 🧠 HYBRID PLAYER PROPS
# --------------------------------------------------

def generate_hybrid_props(game_lines):

    players = ["LeBron James", "Stephen Curry", "Luka Doncic", "Nikola Jokic"]
    stats = ["points", "rebounds", "assists"]

    totals = [g["line"] for g in game_lines if g.get("stat") == "total"]
    avg_total = sum(totals) / len(totals) if totals else 220

    scale = avg_total / 220

    props = []

    for player in players:
        for stat in stats:

            proj = project(player, stat)
            if proj is None:
                continue

            adj_proj = proj * scale

            line = round(adj_proj + random.uniform(-1.5, 1.5), 1)

            props.append({
                "player": player,
                "stat": stat,
                "line": line,
                "book": "hybrid"
            })

    print(f"🧠 HYBRID PROPS: {len(props)} | Avg Total: {round(avg_total,1)}")
    return props

# --------------------------------------------------
# 🔥 FALLBACK
# --------------------------------------------------

def generate_fallback_props():

    players = ["LeBron James", "Stephen Curry", "Luka Doncic", "Nikola Jokic"]
    stats = ["points", "rebounds", "assists"]

    props = []

    for player in players:
        for stat in stats:

            proj = project(player, stat)

            if proj is not None:
                shift = random.uniform(2, 5)
                line = round(proj - shift if random.random() > 0.5 else proj + shift, 1)
            else:
                line = round(random.uniform(5, 30), 1)

            props.append({
                "player": player,
                "stat": stat,
                "line": line,
                "book": "fallback"
            })

    print(f"⚠️ FALLBACK: {len(props)} props")
    return props

# --------------------------------------------------
# 🔥 PROPS ENGINE
# --------------------------------------------------

def build_props():

    # ---------------- FETCH ----------------
    try:
        game_lines = get_odds_props()
    except Exception as e:
        print("❌ ODDS ERROR:", e)
        game_lines = []

    # ---------------- HYBRID ----------------
    if game_lines:
        print(f"📡 USING ODDS API ({len(game_lines)}) → HYBRID MODE")
        raw_props = generate_hybrid_props(game_lines)
    else:
        print("🚨 USING FALLBACK")
        raw_props = generate_fallback_props()

    # ---------------- GROUP ----------------
    try:
        grouped = group_props(raw_props)
        best_lines = get_best_lines(grouped)
    except Exception:
        best_lines = raw_props

    props_out = []

    for p in best_lines:
        try:
            player = p.get("player")
            stat = p.get("stat")
            line = p.get("best_over_line") or p.get("line")

            if not player or not stat or line is None:
                continue

            result = evaluate_prop(player=player, line=line, stat=stat)
            if not result:
                continue

            edge = result.get("edge", 0)

            prob = result.get("probability")
            if prob is None:
                prob = 0.5 + (edge / 15)

            prob = max(min(prob, 0.85), 0.45)

            record_prop_line(player, stat, line)
            clv = update_prop_line(player, stat, line)

            print(
                f"DEBUG → {player} {stat} | "
                f"Edge: {round(edge,2)} | "
                f"Prob: {round(prob,3)} | "
                f"CLV: {clv}"
            )

            # 🔥 DYNAMIC FILTER
            min_edge = 0.25
            min_prob = 0.51

            if len(raw_props) > 1000:
                min_edge = 0.15
                min_prob = 0.50

            if abs(edge) < min_edge or prob < min_prob:
                continue

            size = get_bet_size(
                probability=prob,
                edge_score=abs(edge) * 10,
                bankroll=1000,
                clv=clv
            )

            if size <= 0:
                continue

            result.update({
                "bet_size": size,
                "clv": clv,
                "probability": prob
            })

            key = f"{player}-{stat}-{line}"

            if key not in ALERTED:
                ALERTED.add(key)
                log_prop(result)

                send_smart_alert(
                    player,
                    stat,
                    edge,
                    prob,
                    clv,
                    result.get("bet", "OVER" if edge > 0 else "UNDER"),
                    size
                )

            props_out.append(result)

        except Exception as e:
            print("❌ PROP ERROR:", e)

    print(f"✅ GOOD PROPS: {len(props_out)}")
    return props_out

# --------------------------------------------------
# 🔄 LOOP
# --------------------------------------------------

def build_games():
    return {
        "props": build_props(),
        "timestamp": datetime.utcnow().isoformat()
    }

def refresh_loop():
    global games_cache

    while True:
        try:
            print("\n🔄 SYSTEM UPDATE\n")
            games_cache = build_games()
        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(REFRESH_INTERVAL)

# --------------------------------------------------
# 🚀 STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup():
    print("🚀 SYSTEM STARTED (HYBRID MODE)")
    threading.Thread(target=refresh_loop, daemon=True).start()

# --------------------------------------------------
# 🌐 API
# --------------------------------------------------

@app.get("/")
def root():
    return {"status": "LIVE"}

@app.get("/games")
def games():
    return games_cache or {"status": "loading"}

@app.get("/props")
def props():
    return games_cache.get("props", [])

@app.get("/dashboard")
def dashboard():
    return {
        "roi": calculate_roi() if calculate_roi else {},
        "clv": calculate_clv() if calculate_clv else {},
        "health": model_health() if model_health else "unknown",
        "props_count": len(games_cache.get("props", []))
    }

# --------------------------------------------------
# 🖥 UI
# --------------------------------------------------

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <body style="background:#0f172a;color:white;font-family:sans-serif;padding:20px">
    <h1>🔥 Betting Dashboard</h1>
    <div id="data"></div>

    <script>
    async function load(){
        let d = await fetch('/dashboard').then(r=>r.json());
        let p = await fetch('/props').then(r=>r.json());

        let html = `<h2>ROI: ${d.roi?.roi || 0}%</h2>`;

        p.forEach(x=>{
            html += `<div>
                ${x.player} ${x.stat} | Edge: ${x.edge} | Bet: ${x.bet} | Size: $${x.bet_size}
            </div>`;
        });

        document.getElementById('data').innerHTML = html;
    }

    setInterval(load,3000);
    load();
    </script>
    </body>
    </html>
    """
