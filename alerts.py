import os
import requests
import time

DISCORD_WEBHOOK = os.getenv("https://discord.com/api/webhooks/1483683612468707449/4ZgNWlmDrXRYmivgawM-tTcH2htzwbpR_3LIMZVp8oP85iQcjHZ_zoL2nJaMDehp3UY9")

ENABLE_ALERTS = True
MAX_RETRIES = 3
RETRY_DELAY = 2


def _post(payload):
    if not ENABLE_ALERTS:
        return False

    if not DISCORD_WEBHOOK:
        print("DISCORD_WEBHOOK not set")
        return False

    for _ in range(MAX_RETRIES):
        try:
            res = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

            if res.status_code in (200, 204):
                return True

            if res.status_code == 429:
                retry_after = res.json().get("retry_after", 2)
                time.sleep(retry_after)
                continue

            print(f"Discord status error: {res.status_code} {res.text}")

        except Exception as e:
            print(f"Discord error: {e}")

        time.sleep(RETRY_DELAY)

    return False


def send_discord_alert(message):
    return _post({"content": message})


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
        msg += f"💰 Bet Size: **${bet_size}**\n"

    return _post({"content": msg})


def send_embed_alert(title, fields):
    embed = {
        "title": title,
        "color": 0x00FF99,
        "fields": [
            {"name": str(k), "value": str(v), "inline": True}
            for k, v in fields.items()
        ],
    }
    return _post({"embeds": [embed]})


def send_error_alert(error_msg):
    return _post({"content": f"🚨 ERROR:\n```{error_msg}```"})


def send_edge_alert(game, edge):
    return _post({"content": f"⚡ HIGH EDGE GAME\n{game}\nEdge: {edge}"})