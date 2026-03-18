import random
import json
import os

Q_FILE = "q_table.json"

Q = {}

ACTIONS = ["bet", "skip"]

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1


# -------------------------
# STATE
# -------------------------

def get_state(edge, prob, volatility):
    return (round(edge), round(prob, 2), volatility)


# -------------------------
# LOAD / SAVE
# -------------------------

def load_q():
    global Q
    if os.path.exists(Q_FILE):
        with open(Q_FILE, "r") as f:
            Q = json.load(f)

def save_q():
    with open(Q_FILE, "w") as f:
        json.dump(Q, f)


# -------------------------
# ACTION
# -------------------------

def choose_action(state):

    state = str(state)

    if random.random() < EPSILON:
        return random.choice(ACTIONS)

    if state not in Q:
        Q[state] = {a: 0 for a in ACTIONS}

    return max(Q[state], key=Q[state].get)


# -------------------------
# UPDATE
# -------------------------

def update_q(state, action, reward):

    state = str(state)

    if state not in Q:
        Q[state] = {a: 0 for a in ACTIONS}

    current = Q[state][action]

    Q[state][action] = current + ALPHA * (reward - current)


# -------------------------
# REWARD
# -------------------------

def get_reward(result):

    if result == "win":
        return 1

    if result == "loss":
        return -1

    return 0