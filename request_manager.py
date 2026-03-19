# --------------------------------------------------
# 🔐 REQUEST MANAGER (ELITE STEALTH VERSION)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_RETRIES = 3

PROXY_POOL = [
    # "http://user:pass@ip:port",
]

# --------------------------------------------------
# USER AGENTS (REAL BROWSERS)
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
]

# --------------------------------------------------
# HEADERS (CRITICAL UPGRADE 🔥)
# --------------------------------------------------

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://sportsbook.draftkings.com/",
        "Origin": "https://sportsbook.draftkings.com",
        "Connection": "keep-alive"
    }

# --------------------------------------------------
# SESSION POOL (BIG FIX 🔥)
# --------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update(random_headers())

def rotate_session():
    global SESSION
    SESSION = requests.Session()
    SESSION.headers.update(random_headers())

    if PROXY_POOL:
        proxy = random.choice(PROXY_POOL)
        SESSION.proxies = {"http": proxy, "https": proxy}
        print("🌐 Proxy rotated")

# --------------------------------------------------
# SAFE GET (SMART RETRY)
# --------------------------------------------------

def safe_get(url, params=None, retries=MAX_RETRIES):

    global SESSION

    for attempt in range(retries):

        try:
            # 🔥 human delay
            time.sleep(random.uniform(1.2, 3.5))

            res = SESSION.get(
                url,
                params=params,
                timeout=12
            )

            # ---------------- SUCCESS ----------------
            if res.status_code == 200:
                return res.json()

            # ---------------- BLOCKED ----------------
            if res.status_code in (403, 429):

                print(f"⚠️ Blocked ({res.status_code}) retry {attempt+1}")

                # 🔥 rotate identity
                rotate_session()

                # exponential backoff
                time.sleep(2.5 * (attempt + 1))
                continue

            # ---------------- OTHER ----------------
            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)

            rotate_session()
            time.sleep(2)

    print("🚨 Request failed after retries")
    return None
