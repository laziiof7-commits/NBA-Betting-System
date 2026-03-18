# --------------------------------------------------
# 🔥 ELITE ALERT SYSTEM (SAFE + RETRY + PRODUCTION READY)
# --------------------------------------------------

import os
import requests
import time

# --------------------------------------------------
# CONFIG (FIXED)
# --------------------------------------------------

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

ENABLE_ALERTS = True
MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 10

# auto-disable if no webhook
if not DISCORD_WEBHOOK:
    ENABLE_ALERTS = False
    print("⚠️ Discord alerts disabled (no webhook found)")

# --------------------------------------------------
# CORE POST FUNCTION (SAFE)
# --------------------------------------------------

def _post(payload):

    if not ENABLE_ALERTS:
        return False

    if not DISCORD_WEBHOOK:
        return False

    for attempt in range(MAX_RETRIES):

        try:
            res = requests.post(
                DISCORD_WEBHOOK,
                json=payload,
                timeout=TIMEOUT
            )

            # success
            if res.status_code in (200, 204):
                return True

            # rate limit handling
            if res.status_code == 429:
                retry_after = res.json().get("retry_after", RETRY_DELAY)
                print(f"⏳ Rate limited, retrying in {retry_after}s")
                time.sleep(retry_after)
                continue

            print(f"❌ Discord error {res.status_code}: {res.text}")

        except Exception as e:
            print(f"❌ Discord request failed: {e}")

        time.sleep(RETRY_DELAY)

    return False


# --------------------------------------------------
# 🔔 BASIC MESSAGE ALERT
# --------------------------------------------------

def send_discord_alert(message):

    payload = {
        "content": str(message)[:2000]  # Discord limit
    }

    return _post(payload)


# --------------------------------------------------
# 💰 GAME BET ALERT
# --------------------------------------------------

def send_bet_alert(game, edge, prob, market, model, bet_size=None):

    msg = f"""
🔥 **AUTO BET DETECTED**

🏀 {game}

📊 Edge: **{round(edge, 2)}**
🎯 Prob: **{round(prob, 2)}**
📉 Market: **{market}**
🧠 Model: **{model}**
"""

    if bet_size is not None:
        msg += f"\n💰 Bet Size: **${round(bet_size, 2)}**"

    return send_discord_alert(msg)


# --------------------------------------------------
# 🔥 PROP ALERT (NEW)
# --------------------------------------------------

def send_prop_alert(prop, bet_size=None):

    msg = f"""
🔥 **PROP BET**

👤 {prop['player']} ({prop['stat']})

📊 Line: {prop['line']}
🧠 Projection: {prop['projection']}
📈 Edge: {prop['edge']}
🎯 Prob: {prop['probability']}
💎 Confidence: {prop.get('confidence', 0)}

💰 BET: {prop['bet']}
"""

    if bet_size:
        msg += f"\n💵 Size: ${round(bet_size, 2)}"

    return send_discord_alert(msg)


# --------------------------------------------------
# 📊 EMBED ALERT (CLEAN UI)
# --------------------------------------------------

def send_embed_alert(title, fields):

    payload = {
        "embeds": [
            {
                "title": title,
                "color": 0x00FF99,
                "fields": [
                    {
                        "name": str(k),
                        "value": str(v),
                        "inline": True
                    }
                    for k, v in fields.items()
                ]
            }
        ]
    }

    return _post(payload)


# --------------------------------------------------
# 🚨 ERROR ALERT
# --------------------------------------------------

def send_error_alert(error_msg):

    msg = f"🚨 ERROR:\n```{str(error_msg)[:1800]}```"

    return send_discord_alert(msg)


# --------------------------------------------------
# ⚡ EDGE ALERT
# --------------------------------------------------

def send_edge_alert(game, edge):

    msg = f"""
⚡ **HIGH EDGE GAME**

🏀 {game}

📊 Edge: {round(edge, 2)}
"""

    return send_discord_alert(msg)