# --------------------------------------------------
# 🔥 REQUEST MANAGER (ANTI-BOT ENGINE)
# --------------------------------------------------

import requests
import random
import time

# 🔁 Rotate user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 11)"
]

# 🔌 Add proxies later here
PROXIES = [
    None,  # start without proxy
    # "http://user:pass@ip:port"
]

# --------------------------------------------------
# CREATE SESSION
# --------------------------------------------------

def create_session():

    session = requests.Session()

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://sportsbook.draftkings.com/",
        "Origin": "https://sportsbook.draftkings.com",
        "Connection": "keep-alive"
    }

    session.headers.update(headers)

    proxy = random.choice(PROXIES)

    if proxy:
        session.proxies = {
            "http": proxy,
            "https": proxy
        }

    return session

# --------------------------------------------------
# SAFE REQUEST
# --------------------------------------------------

def safe_get(url):

    session = create_session()

    try:
        time.sleep(random.uniform(2, 5))  # 🔥 human delay

        res = session.get(url, timeout=10)

        if res.status_code == 403:
            print("❌ BLOCKED (403)")
            return None

        if res.status_code != 200:
            print(f"❌ ERROR: {res.status_code}")
            return None

        return res.json()

    except Exception as e:
        print("❌ REQUEST ERROR:", e)
        return None