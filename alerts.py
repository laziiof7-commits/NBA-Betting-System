# --------------------------------------------------
# 🔔 SMART ALERT SYSTEM
# --------------------------------------------------

def send_smart_alert(player, stat, edge, prob, clv, bet, size):

    print(f"""
🔥 BET ALERT

👤 {player}
📊 {stat}
💰 Edge: {round(edge,2)}
🎯 Prob: {prob}
📈 CLV: {clv}
📌 Bet: {bet}
💵 Size: ${size}
""")
