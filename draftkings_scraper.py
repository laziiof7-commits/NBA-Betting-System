# --------------------------------------------------
# 🔥 DRAFTKINGS SCRAPER (STABLE + CLEAN)
# --------------------------------------------------

from request_manager import safe_get

URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/42648?format=json"

# --------------------------------------------------
# CLEAN PLAYER NAME
# --------------------------------------------------

def clean_name(name):
    return (
        str(name)
        .replace(" Jr.", "")
        .replace(" Sr.", "")
        .strip()
    )

# --------------------------------------------------
# PARSE
# --------------------------------------------------

def parse_props(data):

    props = []

    try:
        categories = data.get("eventGroup", {}).get("offerCategories", [])

        for cat in categories:

            subs = cat.get("offerSubcategoryDescriptors", [])

            for sub in subs:

                name = sub.get("name", "").lower()

                # 🔥 only target core stats
                if not any(x in name for x in ["points", "rebounds", "assists"]):
                    continue

                stat = (
                    "points" if "points" in name else
                    "rebounds" if "rebounds" in name else
                    "assists"
                )

                offers = sub.get("offers", [])

                for offer_group in offers:

                    for offer in offer_group:

                        try:
                            outcomes = offer.get("outcomes", [])

                            if not outcomes:
                                continue

                            outcome = outcomes[0]

                            player = clean_name(outcome.get("participant"))
                            line = outcome.get("line")

                            if not player or line is None:
                                continue

                            props.append({
                                "player": player,
                                "stat": stat,
                                "line": float(line),
                                "book": "DraftKings"  # 🔥 REQUIRED
                            })

                        except Exception:
                            continue

    except Exception as e:
        print("❌ DK PARSE ERROR:", e)

    return props

# --------------------------------------------------
# MAIN
# --------------------------------------------------

def get_dk_props():

    data = safe_get(URL)

    if not data:
        print("❌ DK BLOCKED / NO DATA")
        return []

    props = parse_props(data)

    if not props:
        print("⚠️ DK returned 0 props")
    else:
        print(f"📊 DK PROPS: {len(props)}")

    return props
