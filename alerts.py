# --------------------------------------------------
# 🔥 ELITE ALERT SYSTEM (RATE-LIMIT SAFE + QUEUE)
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

# ⛔ GLOBAL RATE LIMIT PROTECTION
ALERT_COOLDOWN = 1.5  # seconds between messages

# --------------------------------------------------
# STATE
# --------------------------------------------------

LAST_ALERT_TIME = 0
ALERT_QUEUE = deque()
QUEUE_RUNNING = False

# --------------------------------------------------
# CORE POST FUNCTION
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

            # ✅ SUCCESS
            if res.status_code in (200, 204):
                return True

            # ⏳ RATE LIMITED
            if res.status_code == 429:
                try:
                    retry_after = res.json().get("retry_after", 2)
                except:
                    retry_after = 2

                print(f"⏳ Discord rate limited, retrying in {retry_after}s")
                time.sleep(retry_after)
                continue

            # ❌ OTHER ERROR
            print(f"❌ Discord status error: {res.status_code} {res.text}")

        except Exception as e:
            print(f"❌ Discord request failed: {e}")

        time.sleep(RETRY_DELAY)

    return False

# --------------------------------------------------
# QUEUE WORKER (ANTI-SPAM SYSTEM)
# --------------------------------------------------

def _queue_worker():

    global LAST_ALERT_TIME, QUEUE_RUNNING

    while ALERT_QUEUE:

        payload = ALERT_QUEUE.popleft()

        now = time.time()

        # ⛔ COOLDOWN ENFORCED
        if now - LAST_ALERT_TIME < ALERT_COOLDOWN:
            sleep_time = ALERT_COOLDOWN - (now - LAST_ALERT_TIME)
            time.sleep(sleep_time)

        success = _post(payload)

        if success:
            LAST_ALERT_TIME = time.time()

    QUEUE_RUNNING = False

# --------------------------------------------------
# SEND ALERT (SAFE ENTRY POINT)
# --------------------------------------------------

def send_discord_alert(message):

    global QUEUE_RUNNING

    payload = {"content": str(message)}

    ALERT_QUEUE.append(payload)

    # 🔁 START WORKER IF NOT RUNNING
    if not QUEUE_RUNNING:
        QUEUE_RUNNING = True
        threading.Thread(target=_queue_worker, daemon=True).start()

    return True

# --------------------------------------------------
# STRUCTURED ALERTS
# --------------------------------------------------

def send_bet_alert(game, edge, prob, market, model, bet_size=None):

    msg = f"""
🔥 **AUTO BET DETECTED**

🏀 {game}

📊 Edge: **{edge}**
🎯 Prob: **{prob}**
📉 Market: **{market}**
🧠 Model: **{model}**
"""

    if bet_size is not None:
        msg += f"\n💰 Bet Size: **${bet_size}**"

    return send_discord_alert(msg)

# --------------------------------------------------
# EMBED ALERTS (CLEAN UI)
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

# --------------------------------------------------
# EDGE ALERT
# --------------------------------------------------

def send_edge_alert(player, stat, edge):

    msg = f"""
⚡ **HIGH EDGE PROP**

👤 {player}
📊 {stat}
💰 Edge: **{edge}**
"""

    return send_discord_alert(msg)
