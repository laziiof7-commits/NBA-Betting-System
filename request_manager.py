# --------------------------------------------------
# 🔐 REQUEST MANAGER (STICKY + GEO TARGETING)
# --------------------------------------------------

import requests
import random
import time
import uuid

MAX_RETRIES = 5

# 🔥 CONFIG
PROXY_USER = "user"
PROXY_PASS = "pass"
PROXY_HOST = "gate.smartproxy.com:7000"

# ---------------- SESSION GENERATION ----------------

CURRENT_SESSION = None
SESSION_CREATED_AT = 0
SESSION_TTL = 60  # seconds

def generate_session():

    global CURRENT_SESSION, SESSION_CREATED_AT

    session_id = str(uuid.uuid4())[:8]

    CURRENT_SESSION = (
        f"http://{PROXY_USER}-country-us-session-{session_id}:"
        f"{PROXY_PASS}@{PROXY_HOST}"
    )

    SESSION_CREATED_AT = time.time()

    print(f"🌐 New Proxy Session: {session_id}")

def get_proxy():

    global CURRENT_SESSION

    # 🔥 rotate session every TTL
    if not CURRENT_SESSION or (time.time() - SESSION_CREATED_AT > SESSION_TTL):
        generate_session()

    return {
        "http": CURRENT_SESSION,
        "https": CURRENT_SESSION
    }

# --------------------------------------------------
# HEADERS
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
]

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sportsbook.draftkings.com/",
        "Origin": "https://sportsbook.draftkings.com"
    }

# --------------------------------------------------
# SAFE GET
# --------------------------------------------------

def safe_get(url, params=None):

    for attempt in range(MAX_RETRIES):

        try:
            time.sleep(random.uniform(2.5, 5.5))  # 🔥 human delay

            res = requests.get(
                url,
                params=params,
                headers=random_headers(),
                proxies=get_proxy(),
                timeout=15
            )

            if res.status_code == 200:
                return res.json()

            if res.status_code in (403, 429):
                print(f"⚠️ BLOCKED retry {attempt+1}")

                # 🔥 force new session on block
                generate_session()

                time.sleep(2 * (attempt + 1))
                continue

            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)
            generate_session()
            time.sleep(2)

    print("🚨 FAILED AFTER RETRIES")
    return None
