# rl_agent.py

import random
import json
import os

Q_TABLE = {}
FILE = "q_table.json"

ACTIONS = ["bet", "skip"]

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.15


# -------------------------------
# STATE
# -------------------------------
def get_state(edge, prob, volatility=0):
    return (round(edge), round(prob, 2), round(volatility))


# -------------------------------
# INIT
# -------------------------------
def init_state(state):
    if state not in Q_TABLE:
        Q_TABLE[state] = {a: 0.0 for a in ACTIONS}


# -------------------------------
# ACTION
# -------------------------------
def choose_action(state):
    init_state(state)

    if random.random() < EPSILON:
        return random.choice(ACTIONS)

    return max(Q_TABLE[state], key=Q_TABLE[state].get)


# -------------------------------
# UPDATE
# -------------------------------
def update_q(state, action, reward):
    init_state(state)

    current = Q_TABLE[state][action]
    new = current + ALPHA * (reward - current)

    Q_TABLE[state][action] = new


# -------------------------------
# REWARD
# -------------------------------
def get_reward(result):

    if result == "win":
        return 1
    if result == "loss":
        return -1

    return 0


# -------------------------------
# SAVE / LOAD
# -------------------------------
def save_q():
    with open(FILE, "w") as f:
        json.dump(Q_TABLE, f)


def load_q():
    global Q_TABLE

    if not os.path.exists(FILE):
        Q_TABLE = {}
        return

    with open(FILE, "r") as f:
        Q_TABLE = json.load(f)