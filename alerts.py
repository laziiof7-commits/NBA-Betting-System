# --------------------------------------------------
# 🔥 ELITE DISCORD ALERT SYSTEM (STABLE + FIXED)
# --------------------------------------------------

import os
import requests
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

ENABLE_ALERTS = True
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# --------------------------------------------------
# CORE REQUEST FUNCTION (ULTRA SAFE)
# --------------------------------------------------

def _post(payload):

    if not ENABLE_ALERTS:
        return False

    if not DISCORD_WEBHOOK:
        print("⚠️ DISCORD_WEBHOOK not set")
        return False

    for attempt in range(MAX_RETRIES):

        try:
            res = requests.post(
                DISCORD_WEBHOOK,
                json=payload,
                timeout=10
            )

            # ✅ SUCCESS
            if res.status_code in (200, 204):
                return True

            # 🔁 RATE LIMIT HANDLING
            if res.status_code == 429:
                try:
                    retry_after = res.json().get("retry_after", RETRY_DELAY)
                except:
                    retry_after = RETRY_DELAY

                print(f"⏳ Discord rate limited, retrying in {retry_after}s")
                time.sleep(retry_after)
                continue

            # ❌ OTHER ERRORS
            try:
                error_text = res.json()
            except:
                error_text = res.text

            print(f"❌ Discord error {res.status_code}: {error_text}")

        except Exception as e:
            print(f"❌ Discord request failed: {e}")

        time.sleep(RETRY_DELAY)

    return False

# --------------------------------------------------
# BASIC MESSAGE ALERT
# --------------------------------------------------

def send_discord_alert(message):

    if not message:
        return False

    payload = {
        "content": str(message)[:1900]  # Discord limit safety
    }

    return _post(payload)

# --------------------------------------------------
# 🔥 PROP ALERT (UPGRADED FORMAT)
# --------------------------------------------------

def send_prop_alert(prop):

    if not prop:
        return False

    try:
        msg = f"""
🔥 **PROP BET**

👤 **{prop.get('player')}**
📊 {prop.get('stat').upper()}

📉 Line: {prop.get('line')}
🧠 Projection: {prop.get('projection')}

📈 Edge: **{prop.get('edge')}**
🎯 Prob: **{prop.get('probability')}**

💰 Bet: **{prop.get('bet')}**
💵 Size: **${prop.get('bet_size', 0)}**
"""

        return send_discord_alert(msg)

    except Exception as e:
        print("❌ PROP ALERT ERROR:", e)
        return False

# --------------------------------------------------
# EMBED ALERT (CLEAN UI)
# --------------------------------------------------

def send_embed_alert(title, fields):

    try:
        embed = {
            "title": str(title),
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

        return _post({"embeds": [embed]})

    except Exception as e:
        print("❌ EMBED ERROR:", e)
        return False

# --------------------------------------------------
# ERROR ALERT
# --------------------------------------------------

def send_error_alert(error_msg):

    msg = f"🚨 ERROR:\n```{error_msg}```"
    return send_discord_alert(msg)

# --------------------------------------------------
# TEST ALERT (USE THIS TO VERIFY)
# --------------------------------------------------

def test_alert():

    return send_discord_alert("🚀 SYSTEM TEST ALERT SUCCESS")
