
# --------------------------------------------------
# 🔥 GRADIENT DESCENT MODEL OPTIMIZER
# --------------------------------------------------

import json
import os
import numpy as np

FILE = "prop_history.json"

# fallback weights
DEFAULT = np.array([0.6, 0.4, 0.5, 1.0])


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_history():

    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        return json.load(f)


# --------------------------------------------------
# BUILD DATASET
# --------------------------------------------------

def build_dataset(data):

    X = []
    y = []

    for p in data:

        if "result" not in p:
            continue

        features = [
            p.get("real", 0),
            p.get("model", 0),
            p.get("trend", 0),
            p.get("nn", 0)
        ]

        label = 1 if p["result"] == "WIN" else 0

        X.append(features)
        y.append(label)

    return np.array(X), np.array(y)


# --------------------------------------------------
# SIGMOID (FOR PROBABILITY)
# --------------------------------------------------

def sigmoid(z):
    return 1 / (1 + np.exp(-z))


# --------------------------------------------------
# LOSS FUNCTION (LOG LOSS)
# --------------------------------------------------

def compute_loss(X, y, w):

    preds = sigmoid(X @ w)

    # avoid log(0)
    preds = np.clip(preds, 1e-6, 1 - 1e-6)

    loss = -np.mean(y * np.log(preds) + (1 - y) * np.log(1 - preds))

    return loss


# --------------------------------------------------
# GRADIENT DESCENT TRAINING
# --------------------------------------------------

def train_weights(epochs=200, lr=0.01):

    data = load_history()

    if len(data) < 50:
        return DEFAULT

    X, y = build_dataset(data)

    if len(X) == 0:
        return DEFAULT

    # initialize weights
    w = np.array([0.5, 0.5, 0.5, 0.5])

    for _ in range(epochs):

        preds = sigmoid(X @ w)

        gradient = X.T @ (preds - y) / len(y)

        w -= lr * gradient

        # keep weights stable
        w = np.clip(w, 0, 2)

    return w


# --------------------------------------------------
# PUBLIC FUNCTION
# --------------------------------------------------

def get_weights():

    w = train_weights()

    return {
        "real": float(w[0]),
        "model": float(w[1]),
        "trend": float(w[2]),
        "nn": float(w[3])
    }