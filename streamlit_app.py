import streamlit as st
import requests
import pandas as pd

from bankroll_manager import get_adjusted_bet_size, should_bet
from clv_tracker import calculate_roi, calculate_clv, profit_curve, model_health

# ==============================
# CONFIG
# ==============================

API_URL = "http://127.0.0.1:8000/games"

st.set_page_config(page_title="NBA Command Center", layout="wide")

# ==============================
# STYLE (MOBILE + CLEAN)
# ==============================

st.markdown("""
<style>
body { background:#0b0f1a; color:white; }

.card {
    background:#11161f;
    border-radius:12px;
    padding:12px;
    margin-bottom:10px;
    border:1px solid #1f2633;
}

.green { color:#00ff9c; }
.red { color:#ff4d4d; }
.yellow { color:#facc15; }

.header {
    font-size:22px;
    font-weight:700;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================

st.markdown("<div class='header'>🏀 NBA Command Center</div>", unsafe_allow_html=True)

# ==============================
# LOAD DATA
# ==============================

@st.cache_data(ttl=5)
def load_data():
    try:
        return requests.get(API_URL).json()
    except:
        return {}

data = load_data()

# ==============================
# 📊 DASHBOARD
# ==============================

roi = calculate_roi()
clv = calculate_clv()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Profit", f"${roi['profit']}")

with col2:
    st.metric("📈 ROI", f"{roi['roi']}%")

with col3:
    st.metric("📊 CLV", clv["avg_clv"])

with col4:
    st.metric("🧠 Model", model_health())

# ==============================
# 📈 PROFIT CURVE
# ==============================

curve = profit_curve()

if curve:
    st.line_chart(curve, height=120)

# ==============================
# FILTERS
# ==============================

col1, col2 = st.columns(2)

with col1:
    show_only_odds = st.toggle("💰 Only games with odds", True)

with col2:
    min_edge = st.slider("📊 Min Edge", 0.0, 10.0, 1.0)

# ==============================
# PROCESS DATA
# ==============================

rows = []

for date, games in data.items():

    for game, g in games.items():

        if "@" not in game:
            continue

        away, home = game.split("@")

        edge = g.get("edge")
        prob = g.get("probability")
        score = g.get("edge_score")
        market = g.get("market_total")

        if show_only_odds and market is None:
            continue

        if edge is not None and edge < min_edge:
            continue

        bet_size = None
        is_bet = False

        if edge and prob and score:

            is_bet = should_bet(
                edge_score=score,
                probability=prob,
                clv_edge=edge
            )

            if is_bet:
                bet_size = get_adjusted_bet_size(
                    probability=prob,
                    edge_score=score,
                    bankroll=1000
                )

        rows.append({
            "Date": date,
            "Game": f"{away} @ {home}",
            "Time": g.get("time"),
            "Market": market,
            "Model": g.get("model_total"),
            "Edge": edge,
            "Prob": prob,
            "Score": score,
            "Bet Size": bet_size,
            "Signal": "🔥" if is_bet else ""
        })

df = pd.DataFrame(rows)

# ==============================
# COLOR LOGIC
# ==============================

def color_edge(val):
    if val is None:
        return ""
    if val > 5:
        return "color:#00ff9c;font-weight:bold"
    elif val > 2:
        return "color:#facc15"
    elif val < 0:
        return "color:#ff4d4d"
    return ""

# ==============================
# DISPLAY MAIN TABLE
# ==============================

st.subheader("📊 Games")

if df.empty:
    st.warning("No games available")
else:
    styled = df.style.applymap(color_edge, subset=["Edge"])
    st.dataframe(styled, use_container_width=True)

# ==============================
# 🔥 TOP BETS PANEL
# ==============================

st.subheader("🔥 Top Bets")