import requests
import random
import time

PROXY = "http://smart-myproxyuser:AwilJama25@proxy.smartproxy.net:3120"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def safe_get(url):

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": "https://sportsbook.draftkings.com/",
        "Origin": "https://sportsbook.draftkings.com"
    }

    try:
        time.sleep(random.uniform(1.5, 4))  # human delay

        res = requests.get(
            url,
            headers=headers,
            proxies={"http": PROXY, "https": PROXY},
            timeout=10
        )

        if res.status_code == 200:
            return res.json()

        if res.status_code in (403, 429):
            print("⚠️ BLOCKED → slowing down")
            time.sleep(5)
            return None

        print("❌ Status:", res.status_code)
        return None

    except Exception as e:
        print("❌ Request error:", e)
        return None
