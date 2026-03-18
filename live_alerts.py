# --------------------------------------------------
# 🔥 REAL-TIME PROP ALERT ENGINE (SNIPER MODE)
# --------------------------------------------------

import time

# safe imports
try:
    from prop_scanner import scan_props
except:
    def scan_props(): return []

try:
    from alerts import send_discord_alert
except:
    def send_discord_alert(msg): print(msg)


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

CHECK_INTERVAL = 15  # seconds
MIN_EDGE = 3
MIN_CONFIDENCE = 0.35

SEEN = set()


# --------------------------------------------------
# FORMAT ALERT
# --------------------------------------------------

def format_alert(p):

    return f"""
🚨 LIVE PROP ALERT

👤 {p['player']} ({p['stat']})
📊 Line: {p['line']}
🧠 Projection: {p['projection']}

📈 Edge: {p['edge']}
🎯 Prob: {p['probability']}
💎 Confidence: {p['confidence']}

🔥 Movement: {p.get('movement', 0)}

💰 BET: {p['bet']}
💵 Size: ${p.get('bet_size', 0)}
"""


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

def run_live_alerts():

    print("🚀 LIVE ALERT SYSTEM STARTED")

    while True:

        try:
            props = scan_props()

            for p in props:

                if not p:
                    continue

                key = f"{p['player']}-{p['stat']}-{p['line']}"

                if key in SEEN:
                    continue

                if (
                    p["edge"] >= MIN_EDGE
                    and p["confidence"] >= MIN_CONFIDENCE
                ):

                    SEEN.add(key)

                    send_discord_alert(format_alert(p))

        except Exception as e:
            print("❌ ALERT ERROR:", e)

        time.sleep(CHECK_INTERVAL)