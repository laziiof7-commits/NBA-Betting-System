# --------------------------------------------------
# 📈 TIME SERIES MODEL (LSTM-LIKE PRO VERSION)
# --------------------------------------------------

import json
import os
import numpy as np

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

HISTORY = {}
MAX_POINTS = 20
SAVE_FILE = "time_series.json"


# --------------------------------------------------
# UPDATE SERIES
# --------------------------------------------------

def update_series(key, value):

    if key not in HISTORY:
        HISTORY[key] = []

    HISTORY[key].append(value)

    # keep last N values
    if len(HISTORY[key]) > MAX_POINTS:
        HISTORY[key] = HISTORY[key][-MAX_POINTS:]


# --------------------------------------------------
# WEIGHTED TREND (RECENCY MATTERS)
# --------------------------------------------------

def weighted_trend(series):

    if len(series) < 5:
        return 0

    weights = np.linspace(0.5, 1.5, len(series))

    diffs = np.diff(series)

    weighted = diffs * weights[1:]

    return np.sum(weighted) / np.sum(weights[1:])


# --------------------------------------------------
# MOMENTUM (SHORT TERM)
# --------------------------------------------------

def momentum(series):

    if len(series) < 3:
        return 0

    return series[-1] - series[-3]


# --------------------------------------------------
# VOLATILITY (STABILITY CHECK)
# --------------------------------------------------

def volatility(series):

    if len(series) < 5:
        return 0

    return np.std(series)


# --------------------------------------------------
# MAIN PREDICTOR
# --------------------------------------------------

def predict_trend(key):

    series = HISTORY.get(key, [])

    if len(series) < 5:
        return 0

    trend = weighted_trend(series)
    mom = momentum(series)
    vol = volatility(series)

    # 🔥 FINAL COMBINATION
    final = (trend * 0.6) + (mom * 0.4)

    # penalize unstable series
    if vol > 10:
        final *= 0.7

    return round(final, 2)


# --------------------------------------------------
# SIGNAL STRENGTH (NEW)
# --------------------------------------------------

def trend_strength(key):

    series = HISTORY.get(key, [])

    if len(series) < 5:
        return 0

    vol = volatility(series)

    if vol == 0:
        return 100

    strength = max(0, 100 - (vol * 5))

    return round(strength, 1)


# --------------------------------------------------
# SAVE / LOAD (IMPORTANT)
# --------------------------------------------------

def save_history():

    with open(SAVE_FILE, "w") as f:
        json.dump(HISTORY, f)


def load_history():

    global HISTORY

    if not os.path.exists(SAVE_FILE):
        return

    with open(SAVE_FILE, "r") as f:
        HISTORY = json.load(f)