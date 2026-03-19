import random
import time
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

PROXY = "http://smart-myproxyuser:AwilJama25@proxy.smartproxy.net:3120"

def stealth_get(url):

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        time.sleep(random.uniform(1.2, 3.5))  # human delay

        res = requests.get(
            url,
            headers=headers,
            proxies={"http": PROXY, "https": PROXY},
            timeout=10
        )

        if res.status_code == 200:
            return res.json()

        if res.status_code in (403, 429):
            print("⚠️ BLOCKED → retrying slower...")
            time.sleep(5)
            return None

        print(f"❌ Status: {res.status_code}")
        return None

    except Exception as e:
        print("❌ Request error:", e)
        return None
