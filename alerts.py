# --------------------------------------------------
# 🔥 ELITE ALERT SYSTEM (PRO MODE)
# --------------------------------------------------

import os
import requests
import time
import threading
from collections import deque

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

ENABLE_ALERTS = True

MAX_RETRIES = 3
RETRY_DELAY = 2

ALERT_COOLDOWN = 1.5  # seconds

# 🔥 FILTER SETTINGS
MIN_EDGE_ALERT = 1.5   # don't alert weak plays
MIN_PROB_ALERT = 0.55

# --------------------------------------------------
# STATE
# --------------------------------------------------

LAST_ALERT_TIME = 0
ALERT_QUEUE = deque()
QUEUE_RUNNING = False

# --------------------------------------------------
# CORE POST
# --------------------------------------------------

def _post(payload):

    if not ENABLE_ALERTS:
        return False

    if not DISCORD_WEBHOOK:
        print("⚠️ DISCORD_WEBHOOK not set")
        return False

    for attempt in range(MAX_RETRIES):

        try:
            res = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

            if res.status_code in (200, 204):
                return True

            if res.status_code == 429:
                try:
                    retry_after = res.json().get("retry_after", 2)
                except:
                    retry_after = 2

                print(f"⏳ Discord rate limited, retrying in {retry_after}s")
                time.sleep(retry_after)
                continue

            print(f"❌ Discord status error: {res.status_code}")

        except Exception as e:
            print(f"❌ Discord request failed: {e}")

        time.sleep(RETRY_DELAY)

    return False

# --------------------------------------------------
# QUEUE WORKER
# --------------------------------------------------

def _queue_worker():

    global LAST_ALERT_TIME, QUEUE_RUNNING

    while ALERT_QUEUE:

        payload = ALERT_QUEUE.popleft()

        now = time.time()

        if now - LAST_ALERT_TIME < ALERT_COOLDOWN:
            time.sleep(ALERT_COOLDOWN - (now - LAST_ALERT_TIME))

        success = _post(payload)

        if success:
            LAST_ALERT_TIME = time.time()

    QUEUE_RUNNING = False

# --------------------------------------------------
# BASE ALERT
# --------------------------------------------------

def send_discord_alert(message):

    global QUEUE_RUNNING

    payload = {"content": str(message)}
    ALERT_QUEUE.append(payload)

    if not QUEUE_RUNNING:
        QUEUE_RUNNING = True
        threading.Thread(target=_queue_worker, daemon=True).start()

    return True

# --------------------------------------------------
# 🔥 SMART BET ALERT (MAIN FUNCTION)
# --------------------------------------------------

def send_smart_alert(player, stat, edge, prob, clv, bet, size):

    # 🚫 FILTER BAD ALERTS
    if abs(edge) < MIN_EDGE_ALERT or prob < MIN_PROB_ALERT:
        return False

    # 🔥 EDGE TIERS
    if abs(edge) > 3:
        tier = "🔥 ELITE PLAY"
    elif abs(edge) > 2:
        tier = "✅ STRONG PLAY"
    else:
        tier = "⚠️ LEAN"

    msg = f"""
{tier}

👤 {player}
📊 {stat} → {bet}

📈 Edge: **{round(edge,2)}**
🎯 Prob: **{round(prob,2)}**
📉 CLV: **{clv}**

💰 Bet Size: **${round(size,2)}**
"""

    return send_discord_alert(msg)

# --------------------------------------------------
# EMBED ALERT (OPTIONAL UI)
# --------------------------------------------------

def send_embed_alert(title, fields):

    embed = {
        "title": title,
        "color": 0x00FF99,
        "fields": [
            {"name": str(k), "value": str(v), "inline": True}
            for k, v in fields.items()
        ],
    }

    payload = {"embeds": [embed]}

    ALERT_QUEUE.append(payload)

    global QUEUE_RUNNING

    if not QUEUE_RUNNING:
        QUEUE_RUNNING = True
        threading.Thread(target=_queue_worker, daemon=True).start()

    return True

# --------------------------------------------------
# ERROR ALERT
# --------------------------------------------------

def send_error_alert(error_msg):

    msg = f"🚨 ERROR:\n```{error_msg}```"
    return send_discord_alert(msg)
