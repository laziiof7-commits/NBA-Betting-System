import requests
import time
import json

# ==============================
# 🔑 CONFIG
# ==============================

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1483665682829676584/O7Qg5ZEzMcz4jm1nWhWVsFTz4JYn5KknTn8Ln1xdZO41vfUT5Ep8hFhuDz9b8loIK9pB"

ENABLE_ALERTS = True
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


# ==============================
# 🧠 CORE SENDER
# ==============================

def _post(payload):
    for attempt in range(MAX_RETRIES):
        try:
            res = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

            # success
            if res.status_code in [200, 204]:
                return True

            # rate limited
            if res.status_code == 429:
                retry_after = res.json().get("retry_after", 2)
                time.sleep(retry_after)
                continue

        except Exception as e:
            print(f"Discord error: {e}")

        time.sleep(RETRY_DELAY)

    return False


# ==============================
# 🔔 SIMPLE ALERT
# ==============================

def send_discord_alert(message):
    if not ENABLE_ALERTS:
        return

    payload = {
        "content": message
    }

    _post(payload)


# ==============================
# 🔥 BET ALERT (MAIN FEATURE)
# ==============================

def send_bet_alert(game, edge, prob, market, model, bet_size=None):

    if not ENABLE_ALERTS:
        return

    msg = f"""
🔥 **AUTO BET DETECTED**

🏀 {game}

📊 Edge: **{edge}**
🎯 Prob: **{prob}**
📉 Market: **{market}**
🧠 Model: **{model}**
"""

    if bet_size:
        msg += f"💰 Bet Size: **${bet_size}**\n"

    payload = {
        "content": msg
    }

    _post(payload)


# ==============================
# 💎 EMBED ALERT (PREMIUM LOOK)
# ==============================

def send_embed_alert(title, fields):

    if not ENABLE_ALERTS:
        return

    embed = {
        "title": title,
        "color": 0x00ff99,
        "fields": [
            {"name": k, "value": str(v), "inline": True}
            for k, v in fields.items()
        ]
    }

    payload = {
        "embeds": [embed]
    }

    _post(payload)


# ==============================
# 🚨 ERROR ALERT
# ==============================

def send_error_alert(error_msg):

    if not ENABLE_ALERTS:
        return

    payload = {
        "content": f"🚨 ERROR:\n```{error_msg}```"
    }

    _post(payload)


# ==============================
# 📊 EDGE THRESHOLD ALERT
# ==============================

def send_edge_alert(game, edge):

    if not ENABLE_ALERTS:
        return

    payload = {
        "content": f"⚡ HIGH EDGE GAME\n{game}\nEdge: {edge}"
    }

    _post(payload)