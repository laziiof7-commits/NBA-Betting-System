# --------------------------------------------------
# 🔐 REQUEST MANAGER (STABLE + STEALTH + NO CIRCULAR)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_RETRIES = 3

# 🔥 ADD YOUR PROXIES HERE (OPTIONAL)
PROXY_POOL = [
    # "http://user:pass@ip:port",
]

# --------------------------------------------------
# USER AGENTS
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
    }

# --------------------------------------------------
# SESSION
# --------------------------------------------------

def create_session():

    session = requests.Session()
    session.headers.update(random_headers())

    # 🔥 apply proxy if available
    if PROXY_POOL:
        proxy = random.choice(PROXY_POOL)
        session.proxies = {
            "http": proxy,
            "https": proxy
        }
        print("🌐 Proxy used")

    return session

# --------------------------------------------------
# SAFE GET (RETRY + STEALTH)
# --------------------------------------------------

def safe_get(url, params=None, retries=MAX_RETRIES):

    for attempt in range(retries):

        try:
            session = create_session()

            # 🔥 human-like delay
            time.sleep(random.uniform(0.8, 2.2))

            res = session.get(
                url,
                params=params,
                timeout=10
            )

            # ---------------- SUCCESS ----------------
            if res.status_code == 200:
                try:
                    return res.json()
                except:
                    print("⚠️ JSON decode failed")
                    return None

            # ---------------- BLOCKED ----------------
            if res.status_code in (403, 429):
                print(f"⚠️ Blocked ({res.status_code}) retry {attempt+1}")
                time.sleep(2 * (attempt + 1))
                continue

            # ---------------- OTHER ----------------
            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)
            time.sleep(1.5)

    print("🚨 Request failed after retries")
    return None
