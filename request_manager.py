# --------------------------------------------------
# 🔐 REQUEST MANAGER (STEALTH + PROXY + RETRIES)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_RETRIES = 5
BASE_DELAY = 1.5

# 🔥 ADD YOUR PROXIES HERE
PROXIES = [
    # "http://user:pass@ip:port",
]

# --------------------------------------------------
# REALISTIC HEADERS (IMPORTANT 🔥)
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
        "Origin": "https://sportsbook.draftkings.com",
        "Referer": "https://sportsbook.draftkings.com/",
    }

# --------------------------------------------------
# SESSION (REUSE = HUGE 🔥)
# --------------------------------------------------

SESSION = None

def get_session():

    global SESSION

    if SESSION is None:
        SESSION = requests.Session()
        SESSION.headers.update(random_headers())

    return SESSION

# --------------------------------------------------
# PROXY ROTATION
# --------------------------------------------------

def get_proxy():

    if not PROXIES:
        return None

    proxy = random.choice(PROXIES)

    return {
        "http": proxy,
        "https": proxy
    }

# --------------------------------------------------
# SAFE REQUEST
# --------------------------------------------------

def safe_get(url, params=None):

    session = get_session()

    for attempt in range(MAX_RETRIES):

        try:
            # 🔥 human delay
            time.sleep(random.uniform(1.5, 3.5))

            res = session.get(
                url,
                params=params,
                headers=random_headers(),
                proxies=get_proxy(),
                timeout=12
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

                print(f"⚠️ Blocked ({res.status_code}) retry {attempt+1}")

                # 🔥 rotate identity
                session.headers.update(random_headers())

                # 🔥 exponential backoff
                sleep_time = BASE_DELAY * (attempt + 1) * random.uniform(1.2, 2.0)
                time.sleep(sleep_time)

                continue

            # ---------------- OTHER ----------------
            print(f"❌ Status: {res.status_code}")
            return None

        except Exception as e:

            print("❌ Request error:", e)
            time.sleep(BASE_DELAY * (attempt + 1))

    print("🚨 Request failed after retries")
    return None
