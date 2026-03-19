# --------------------------------------------------
# 🔐 REQUEST MANAGER (FIXED PROXY + STABLE)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_RETRIES = 5

# 🔥 REPLACE WITH YOUR REAL CREDENTIALS
PROXY_USER = "YOUR_USERNAME"
PROXY_PASS = "YOUR_PASSWORD"
PROXY_HOST = "gate.smartproxy.com:7000"

PROXY = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}"

# --------------------------------------------------
# HEADERS
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
]

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://sportsbook.draftkings.com/",
        "Origin": "https://sportsbook.draftkings.com"
    }

# --------------------------------------------------
# PROXY HANDLER (FIXED)
# --------------------------------------------------

def get_proxy():
    return {
        "http": PROXY,
        "https": PROXY
    }

# --------------------------------------------------
# SAFE GET (STEALTH + RETRIES)
# --------------------------------------------------

def safe_get(url, params=None):

    for attempt in range(MAX_RETRIES):

        try:
            # 🔥 human delay
            time.sleep(random.uniform(2.5, 4.5))

            res = requests.get(
                url,
                params=params,
                headers=random_headers(),
                proxies=get_proxy(),
                timeout=15
            )

            # ---------------- SUCCESS ----------------
            if res.status_code == 200:
                try:
                    return res.json()
                except:
                    print("⚠️ JSON decode error")
                    return None

            # ---------------- BLOCKED ----------------
            if res.status_code in (403, 429):
                print(f"⚠️ BLOCKED retry {attempt+1}")
                time.sleep(2 * (attempt + 1))
                continue

            # ---------------- OTHER ----------------
            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)
            time.sleep(2)

    print("🚨 FAILED AFTER RETRIES")
    return None
