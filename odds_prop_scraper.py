# --------------------------------------------------
# 🔥 ODDS PROP SCRAPER (STEALTH + UNIFIED)
# --------------------------------------------------

from results_manager import safe_get
import time

# --------------------------------------------------
# PRIZEPICKS
# --------------------------------------------------

def get_prizepicks():

    url = "https://api.prizepicks.com/projections"

    data = safe_get(url)

    if not data:
        print("🚨 PrizePicks failed after retries")
        return []

    props = []

    try:
        included = {i["id"]: i for i in data.get("included", [])}

        for item in data.get("data", []):

            attr = item.get("attributes", {})
            player_id = item.get("relationships", {}).get("new_player", {}).get("data", {}).get("id")

            player = included.get(player_id, {}).get("attributes", {}).get("name")

            stat = attr.get("stat_type")
            line = attr.get("line_score")

            if not player or not stat or line is None:
                continue

            props.append({
                "player": player,
                "stat": stat.lower(),
                "line": float(line),
                "book": "PrizePicks"
            })

        print(f"✅ PrizePicks props pulled: {len(props)}")

    except Exception as e:
        print("❌ PP parse error:", e)

    return props

# --------------------------------------------------
# DRAFTKINGS
# --------------------------------------------------

def get_draftkings():

    url = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648?format=json"

    data = safe_get(url)

    if not data:
        print("❌ DK BLOCKED / NO DATA")
        return []

    props = []

    try:
        events = data.get("eventGroup", {}).get("events", [])
        offers = data.get("eventGroup", {}).get("offerCategories", [])

        for cat in offers:
            for sub in cat.get("offerSubcategoryDescriptors", []):
                for offer_row in sub.get("offerSubcategory", {}).get("offers", []):

                    for offer in offer_row:

                        label = offer.get("label", "")
                        outcomes = offer.get("outcomes", [])

                        for o in outcomes:

                            player = o.get("participant")
                            line = o.get("line")

                            if not player or line is None:
                                continue

                            # detect stat
                            stat = "points"
                            if "rebounds" in label.lower():
                                stat = "rebounds"
                            elif "assists" in label.lower():
                                stat = "assists"

                            props.append({
                                "player": player,
                                "stat": stat,
                                "line": float(line),
                                "book": "DraftKings"
                            })

        print(f"📊 DraftKings props: {len(props)}")

    except Exception as e:
        print("❌ DK parse error:", e)

    return props

# --------------------------------------------------
# 🔥 MAIN ENTRY
# --------------------------------------------------

def get_odds_props():

    all_props = []

    # ---------------- PRIZEPICKS ----------------
    try:
        pp = get_prizepicks()
        print(f"📊 PrizePicks: {len(pp)}")
        all_props.extend(pp)
    except Exception as e:
        print("❌ PP ERROR:", e)

    time.sleep(2)

    # ---------------- DRAFTKINGS ----------------
    try:
        dk = get_draftkings()
        print(f"📊 DraftKings: {len(dk)}")
        all_props.extend(dk)
    except Exception as e:
        print("❌ DK ERROR:", e)

    # ---------------- FALLBACK ----------------
    if not all_props:
        print("🚨 NO BOOKS AVAILABLE")

    print(f"📊 TOTAL PROPS COMBINED: {len(all_props)}")

    return all_props
