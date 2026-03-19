# --------------------------------------------------
# 🔐 REQUEST MANAGER (NO CIRCULAR IMPORTS)
# --------------------------------------------------

import requests
import random
import time

# --------------------------------------------------
# RANDOM HEADERS (ANTI-BLOCK)
# --------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Connection": "keep-alive"
    }

# --------------------------------------------------
# SESSION
# --------------------------------------------------

def create_session():
    s = requests.Session()
    s.headers.update(random_headers())
    return s

# --------------------------------------------------
# SAFE GET (RETRY + ANTI-BLOCK)
# --------------------------------------------------

def safe_get(url, params=None, retries=3):

    for attempt in range(retries):

        try:
            res = requests.get(
                url,
                params=params,
                headers=random_headers(),
                timeout=8
            )

            if res.status_code == 200:
                return res.json()

            if res.status_code in (403, 429):
                time.sleep(1.5 * (attempt + 1))
                continue

            return None

        except Exception:
            time.sleep(1)

    return None
