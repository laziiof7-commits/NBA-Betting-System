# --------------------------------------------------
# 🔐 STEALTH REQUEST MANAGER (ANTI-BLOCK + PROXY FIX)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_RETRIES = 3

# ✅ WORKING PROXY (DO NOT CHANGE)
PROXY = "http://smart-myproxyuser:AwilTama25@proxy.smartproxy.net:3120"

# --------------------------------------------------
# USER AGENTS (REAL BROWSERS)
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
]

# --------------------------------------------------
# HEADER GENERATOR
# --------------------------------------------------

def build_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://sportsbook.draftkings.com",
        "Referer": "https://sportsbook.draftkings.com/",
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }

# --------------------------------------------------
# SESSION CREATOR (IMPORTANT)
# --------------------------------------------------

def create_session():
    session = requests.Session()
    session.headers.update(build_headers())
    return session

# --------------------------------------------------
# 🔥 STEALTH GET REQUEST
# --------------------------------------------------

def safe_get(url, params=None):

    for attempt in range(MAX_RETRIES):

        try:
            session = create_session()

            # 🧠 human-like delay + escalation
            delay = random.uniform(2, 5) + (attempt * 2)
            time.sleep(delay)

            res = session.get(
                url,
                params=params,
                proxies={
                    "http": PROXY,
                    "https": PROXY
                },
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
                print(f"⚠️ BLOCKED → attempt {attempt+1}")
                time.sleep(5 + attempt * 2)
                continue

            # ---------------- OTHER ----------------
            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)
            time.sleep(2 + attempt)

    print("🚨 FAILED AFTER RETRIES")
    return None

# --------------------------------------------------
# 🔥 ADVANCED GET (OPTIONAL: ROTATE SESSION)
# --------------------------------------------------

def safe_get_rotating(url, params=None):

    session = create_session()

    for attempt in range(MAX_RETRIES):

        try:
            delay = random.uniform(2, 6)
            time.sleep(delay)

            res = session.get(
                url,
                params=params,
                proxies={
                    "http": PROXY,
                    "https": PROXY
                },
                timeout=10
            )

            if res.status_code == 200:
                return res.json()

            if res.status_code in (403, 429):
                print("⚠️ ROTATION BLOCK → refreshing session")
                session = create_session()
                continue

        except Exception as e:
            print("❌ Rotating error:", e)

    return None