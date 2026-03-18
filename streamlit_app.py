import streamlit as st
import requests
import pandas as pd
import time

from bankroll_manager import get_adjusted_bet_size, should_bet
from clv_tracker import calculate_roi, calculate_clv, profit_curve, model_health
from prop_tracker import summary

# ==============================
# CONFIG
# ==============================

API_URL = "http://127.0.0.1:8000/games"

st.set_page_config(page_title="NBA Command Center", layout="wide")

# ==============================
# STYLE
# ==============================

st.markdown("""
<style>
body { background:#0b0f1a; color:white; }

.header {
    font-size:24px;
    font-weight:800;
    margin-bottom:10px;
}

.green { color:#00ff9c; }
.red { color:#ff4d4d; }
.yellow { color:#facc15; }

.block {
    background:#11161f;
    padding:10px;
    border-radius:10px;
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
        return requests.get(API_URL, timeout=3).json()
    except:
        return {}

data = load_data()

# ==============================
# METRICS
# ==============================

roi = calculate_roi()
clv = calculate_clv()
tracker = summary()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Profit", f"${roi['profit']}")
col2.metric("📈 ROI", f"{roi['roi']}%")
col3.metric("📊 CLV", clv["avg_clv"])
col4.metric("🧠 Model", model_health())

col5, col6 = st.columns(2)
col5.metric("🎯 Hit Rate", f"{round(tracker['hit_rate']*100,1)}%")
col6.metric("⚡ Recent Form", f"{round(tracker.get('recent_hit_rate',0.55)*100,1)}%")

# ==============================
# PROFIT CURVE
# ==============================

curve = profit_curve()
if curve:
    st.line_chart(curve, height=120)

# ==============================
# TABS
# ==============================

tab1, tab2, tab3 = st.tabs(["📊 Games", "🔥 Props", "🧠 Analytics"])

# =========================================================
# 📊 GAMES TAB
# =========================================================

with tab1:

    col1, col2 = st.columns(2)

    show_only_odds = col1.toggle("💰 Only games w/ odds", True)
    min_edge = col2.slider("📊 Min Edge", 0.0, 10.0, 1.0)

    rows = []

    for date, games in data.items():

        if date == "props":
            continue

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

                is_bet = should_bet(score, prob, edge)

                if is_bet:
                    bet_size = get_adjusted_bet_size(prob, score, 1000)

            rows.append({
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

    if df.empty:
        st.warning("No games available")
    else:
        st.dataframe(df.sort_values("Edge", ascending=False), use_container_width=True)

    st.subheader("🔥 Top Bets")

    if not df.empty:
        st.dataframe(df.sort_values("Edge", ascending=False).head(5), use_container_width=True)

# =========================================================
# 🔥 PROPS TAB
# =========================================================

with tab2:

    props = data.get("props", [])

    if not props:
        st.warning("No props available")
    else:

        df_props = pd.DataFrame(props)

        # sort by score / edge
        if "score" in df_props.columns:
            df_props = df_props.sort_values("score", ascending=False)

        st.dataframe(df_props, use_container_width=True)

# =========================================================
# 🧠 ANALYTICS TAB
# =========================================================

with tab3:

    st.subheader("📈 Edge Performance")

    edge_data = tracker.get("edge_performance", {})
    if edge_data:
        df_edge = pd.DataFrame(
            [{"Edge": k, "Win Rate": v} for k, v in edge_data.items()]
        )
        st.dataframe(df_edge.sort_values("Edge"), use_container_width=True)

    st.subheader("👤 Player Performance")

    player_data = tracker.get("player_performance", {})
    if player_data:
        df_player = pd.DataFrame(
            [{"Player": k, "Win Rate": v} for k, v in player_data.items()]
        )
        st.dataframe(df_player.sort_values("Win Rate", ascending=False), use_container_width=True)

    st.subheader("📊 Stat Performance")

    stat_data = tracker.get("stat_performance", {})
    if stat_data:
        df_stat = pd.DataFrame(
            [{"Stat": k, "Win Rate": v} for k, v in stat_data.items()]
        )
        st.dataframe(df_stat.sort_values("Win Rate", ascending=False), use_container_width=True)

# ==============================
# AUTO REFRESH
# ==============================

time.sleep(10)
st.rerun()