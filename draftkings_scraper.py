# --------------------------------------------------
# 🔥 DRAFTKINGS SCRAPER (HARDENED + STABLE)
# --------------------------------------------------

import requests
import time
import random

URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648?format=json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://sportsbook.draftkings.com/",
    "Origin": "https://sportsbook.draftkings.com",
    "Connection": "keep-alive"
}

# --------------------------------------------------
# SAFE REQUEST
# --------------------------------------------------

def fetch_data():

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        time.sleep(random.uniform(1.5, 3.5))  # 🔥 anti-bot delay

        res = session.get(URL, timeout=10)

        if res.status_code == 403:
            print("❌ DK BLOCKED (403)")
            return None

        if res.status_code != 200:
            print(f"❌ DK ERROR: {res.status_code}")
            return None

        return res.json()

    except Exception as e:
        print("❌ DK FETCH ERROR:", e)
        return None


# --------------------------------------------------
# PARSE
# --------------------------------------------------

def parse_props(data):

    props = []

    try:
        categories = data.get("eventGroup", {}).get("offerCategories", [])

        for cat in categories:

            for sub in cat.get("offerSubcategoryDescriptors", []):

                name = sub.get("name", "").lower()

                if not any(x in name for x in ["points", "rebounds", "assists"]):
                    continue

                stat = (
                    "points" if "points" in name else
                    "rebounds" if "rebounds" in name else
                    "assists"
                )

                for offer in sub.get("offers", []):

                    for o in offer:

                        try:
                            outcome = o["outcomes"][0]

                            player = outcome.get("participant")
                            line = outcome.get("line")

                            if not player or line is None:
                                continue

                            props.append({
                                "player": player,
                                "stat": stat,
                                "line": float(line)
                            })

                        except:
                            continue

    except Exception as e:
        print("❌ PARSE ERROR:", e)

    return props


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def get_dk_props():

    data = fetch_data()

    if not data:
        return []

    props = parse_props(data)

    print(f"📊 DraftKings props: {len(props)}")

    return props
