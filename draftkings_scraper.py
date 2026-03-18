# --------------------------------------------------
# 🔥 DRAFTKINGS PROP SCRAPER (REAL DATA)
# --------------------------------------------------

import requests

# DraftKings NBA event group (props)
URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648?format=json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

# --------------------------------------------------
# PARSE PROPS
# --------------------------------------------------

def parse_dk_props(data):

    props = []

    try:
        event_group = data.get("eventGroup", {})
        events = event_group.get("events", [])
        markets = event_group.get("offerCategories", [])

        for category in markets:

            for subcat in category.get("offerSubcategoryDescriptors", []):

                name = subcat.get("name", "").lower()

                # 🔥 FILTER ONLY KEY STATS
                if not any(x in name for x in ["points", "rebounds", "assists"]):
                    continue

                stat = None
                if "points" in name:
                    stat = "points"
                elif "rebounds" in name:
                    stat = "rebounds"
                elif "assists" in name:
                    stat = "assists"

                for offer in subcat.get("offers", []):

                    for o in offer:

                        try:
                            player = o["outcomes"][0]["participant"]
                            line = o["outcomes"][0]["line"]

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
        print("❌ DK PARSE ERROR:", e)

    return props


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def get_dk_props():

    try:
        res = requests.get(URL, headers=HEADERS, timeout=8)

        if res.status_code != 200:
            print("❌ DK ERROR:", res.status_code)
            return []

        data = res.json()

        props = parse_dk_props(data)

        print(f"📊 DraftKings props: {len(props)}")

        return props

    except Exception as e:
        print("❌ DK FETCH ERROR:", e)
        return []