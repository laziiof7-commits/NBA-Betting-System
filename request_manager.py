# --------------------------------------------------
# 🔐 REQUEST MANAGER (RESIDENTIAL PROXY MODE)
# --------------------------------------------------

import requests
import random
import time

MAX_RETRIES = 5

PROXY = "http://user:pass@gate.smartproxy.com:7000"

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

def safe_get(url, params=None):

    for attempt in range(MAX_RETRIES):

        try:
            time.sleep(random.uniform(2, 4))  # human delay

            res = requests.get(
                url,
                params=params,
                headers=random_headers(),
                proxies={
                    "http": PROXY,
                    "https": PROXY
                },
                timeout=15
            )

            if res.status_code == 200:
                return res.json()

            if res.status_code in (403, 429):
                print(f"⚠️ BLOCKED retry {attempt+1}")
                time.sleep(2 * (attempt + 1))
                continue

            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:
            print("❌ Request error:", e)
            time.sleep(2)

    print("🚨 FAILED AFTER RETRIES")
    return None
