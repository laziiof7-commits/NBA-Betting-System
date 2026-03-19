# --------------------------------------------------
# 🔥 DRAFTKINGS SCRAPER (UNBLOCKED VERSION)
# --------------------------------------------------

from request_manager import safe_get
import random
import time

URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648?format=json"

# --------------------------------------------------
# STEALTH DELAY
# --------------------------------------------------

def stealth_delay():
    time.sleep(random.uniform(1.5, 4.0))

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

                            line = outcome.get("line")

                            if line is None:
                                continue

                            props.append({
                                "player": outcome.get("participant"),
                                "stat": stat,
                                "line": float(line),
                                "book": "draftkings"
                            })

                        except:
                            continue

    except Exception as e:
        print("❌ DK PARSE ERROR:", e)

    return props

# --------------------------------------------------
# MAIN (RETRY + STEALTH)
# --------------------------------------------------

def get_dk_props():

    for attempt in range(3):

        stealth_delay()

        data = safe_get(URL)

        if data:
            props = parse_props(data)

            if props:
                print(f"📊 DK PROPS: {len(props)}")
                return props

        print(f"⚠️ DK retry {attempt+1}")

    print("❌ DK BLOCKED / NO DATA")
    return []
