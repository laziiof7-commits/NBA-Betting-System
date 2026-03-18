import numpy as np
import json
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MODEL_FILE = "nn_weights.json"

INPUT_SIZE = 5
LEARNING_RATE = 0.0001

# --------------------------------------------------
# INIT
# --------------------------------------------------

weights = np.random.randn(INPUT_SIZE) * 0.1
bias = 0.0


# --------------------------------------------------
# ACTIVATION
# --------------------------------------------------

def relu(x):
    return np.maximum(0, x)


def relu_derivative(x):
    return (x > 0).astype(float)


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize(features):

    # simple scaling
    return np.array(features) / 100


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

def predict_nn(features):

    x = normalize(features)

    z = np.dot(x, weights) + bias
    output = relu(z)

    return float(output) * 100  # scale back


# --------------------------------------------------
# TRAINING (KEY UPGRADE)
# --------------------------------------------------

def train_nn(features, actual):

    global weights, bias

    x = normalize(features)

    # forward
    z = np.dot(x, weights) + bias
    pred = relu(z)

    error = actual - pred

    # backward
    grad = relu_derivative(z)

    weights += LEARNING_RATE * error * grad * x
    bias += LEARNING_RATE * error * grad


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

def save_model():

    data = {
        "weights": weights.tolist(),
        "bias": bias
    }

    with open(MODEL_FILE, "w") as f:
        json.dump(data, f)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def load_model():

    global weights, bias

    if not os.path.exists(MODEL_FILE):
        return

    with open(MODEL_FILE, "r") as f:
        data = json.load(f)

        weights = np.array(data["weights"])
        bias = data["bias"]