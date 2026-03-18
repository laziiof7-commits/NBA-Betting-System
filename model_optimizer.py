# --------------------------------------------------
# 🔥 ELITE MODEL OPTIMIZER (GRADIENT DESCENT + SMART LEARNING)
# --------------------------------------------------

import json
import os
import numpy as np

FILE = "prop_history.json"

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MIN_DATA = 50
EPOCHS = 300
BASE_LR = 0.01
REG_LAMBDA = 0.001  # regularization strength

DEFAULT_WEIGHTS = np.array([0.5, 0.3, 0.1, 0.1])


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_history():

    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []


# --------------------------------------------------
# BUILD DATASET
# --------------------------------------------------

def build_dataset(data):

    X = []
    y = []

    for p in data:

        if p.get("result") not in ["WIN", "LOSS"]:
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

    if not X:
        return None, None

    return np.array(X, dtype=float), np.array(y, dtype=float)


# --------------------------------------------------
# FEATURE NORMALIZATION (CRITICAL 🔥)
# --------------------------------------------------

def normalize_features(X):

    if X is None or len(X) == 0:
        return X

    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)

    std[std == 0] = 1  # prevent division by zero

    return (X - mean) / std


# --------------------------------------------------
# SIGMOID
# --------------------------------------------------

def sigmoid(z):
    return 1 / (1 + np.exp(-z))


# --------------------------------------------------
# LOSS FUNCTION (LOG LOSS + REGULARIZATION)
# --------------------------------------------------

def compute_loss(X, y, w):

    preds = sigmoid(X @ w)
    preds = np.clip(preds, 1e-6, 1 - 1e-6)

    loss = -np.mean(y * np.log(preds) + (1 - y) * np.log(1 - preds))

    # 🔥 L2 REGULARIZATION
    reg = REG_LAMBDA * np.sum(w ** 2)

    return loss + reg


# --------------------------------------------------
# TRAINING (ADAPTIVE GRADIENT DESCENT)
# --------------------------------------------------

def train_weights():

    data = load_history()

    if len(data) < MIN_DATA:
        return DEFAULT_WEIGHTS

    X, y = build_dataset(data)

    if X is None or len(X) < MIN_DATA:
        return DEFAULT_WEIGHTS

    X = normalize_features(X)

    # initialize weights
    w = np.array([0.5, 0.5, 0.5, 0.5], dtype=float)

    lr = BASE_LR

    prev_loss = float("inf")

    for epoch in range(EPOCHS):

        preds = sigmoid(X @ w)

        # gradient
        gradient = (X.T @ (preds - y)) / len(y)

        # regularization gradient
        gradient += 2 * REG_LAMBDA * w

        # update
        w -= lr * gradient

        # clip weights (stability)
        w = np.clip(w, 0, 3)

        # adaptive learning rate
        loss = compute_loss(X, y, w)

        if loss > prev_loss:
            lr *= 0.7  # reduce if worse
        else:
            lr *= 1.02  # slightly increase if improving

        prev_loss = loss

    return w


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def get_weights():

    w = train_weights()

    total = np.sum(w)

    if total == 0:
        return {
            "real": 0.5,
            "model": 0.3,
            "trend": 0.1,
            "nn": 0.1
        }

    # 🔥 normalize weights to sum = 1
    w = w / total

    return {
        "real": round(float(w[0]), 3),
        "model": round(float(w[1]), 3),
        "trend": round(float(w[2]), 3),
        "nn": round(float(w[3]), 3)
    }
