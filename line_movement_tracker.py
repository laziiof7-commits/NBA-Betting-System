# --------------------------------------------------
# 🔥 LINE MOVEMENT TRACKER (CLV + STEAM)
# --------------------------------------------------

import json
import os
from datetime import datetime

FILE = "line_movement.json"

# --------------------------------------------------
# LOAD / SAVE
# --------------------------------------------------

def load_data():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------------------------------
# TRACK LINES
# --------------------------------------------------

def update_line(player, stat, line):

    data = load_data()

    key = f"{player}_{stat}"

    if key not in data:
        data[key] = []

    data[key].append({
        "line": line,
        "time": datetime.utcnow().isoformat()
    })

    # keep last 20
    data[key] = data[key][-20:]

    save_data(data)

# --------------------------------------------------
# GET MOVEMENT
# --------------------------------------------------

def get_movement(player, stat):

    data = load_data()
    key = f"{player}_{stat}"

    series = data.get(key, [])

    if len(series) < 2:
        return 0

    return round(series[-1]["line"] - series[0]["line"], 2)

# --------------------------------------------------
# STEAM DETECTION
# --------------------------------------------------

def is_steam_move(player, stat):

    move = get_movement(player, stat)

    return abs(move) >= 2  # sharp threshold