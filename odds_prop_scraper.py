# --------------------------------------------------
# 🔥 MULTI-BOOK PROP SCRAPER (FINAL VERSION)
# --------------------------------------------------

def safe_import(module, func):
    try:
        m = __import__(module, fromlist=[func])
        return getattr(m, func)
    except Exception as e:
        print(f"⚠️ Import failed: {module} -> {e}")
        return None

# ---------------- LOAD SCRAPERS ----------------

get_pp = safe_import("prizepicks_scraper", "get_prizepicks_props")
get_dk = safe_import("draftkings_scraper", "get_dk_props")
get_fd = safe_import("fanduel_scraper", "get_fd_props")

# --------------------------------------------------
# 🔥 NORMALIZE PROP
# --------------------------------------------------

def normalize_prop(p, book):

    try:
        return {
            "player": str(p.get("player")).strip(),
            "stat": str(p.get("stat")).lower().strip(),
            "line": float(p.get("line")),
            "book": book
        }
    except:
        return None

# --------------------------------------------------
# 🔥 DEDUPLICATION
# --------------------------------------------------

def dedupe_props(props):

    seen = set()
    unique = []

    for p in props:
        key = (p["player"], p["stat"], p["line"], p["book"])

        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique

# --------------------------------------------------
# 🔥 MAIN FUNCTION
# --------------------------------------------------

def get_odds_props():

    all_props = []

    # ---------------- PRIZEPICKS ----------------
    if get_pp:
        try:
            props = get_pp()
            if props:
                print(f"📊 PrizePicks: {len(props)}")

                for p in props:
                    norm = normalize_prop(p, "PrizePicks")
                    if norm:
                        all_props.append(norm)

        except Exception as e:
            print("❌ PP error:", e)

    # ---------------- DRAFTKINGS ----------------
    if get_dk:
        try:
            props = get_dk()
            if props:
                print(f"📊 DraftKings: {len(props)}")

                for p in props:
                    norm = normalize_prop(p, "DraftKings")
                    if norm:
                        all_props.append(norm)

        except Exception as e:
            print("❌ DK error:", e)

    # ---------------- FANDUEL ----------------
    if get_fd:
        try:
            props = get_fd()
            if props:
                print(f"📊 FanDuel: {len(props)}")

                for p in props:
                    norm = normalize_prop(p, "FanDuel")
                    if norm:
                        all_props.append(norm)

        except Exception as e:
            print("❌ FD error:", e)

    # ---------------- FINAL ----------------

    if not all_props:
        print("🚨 NO BOOKS AVAILABLE → fallback")
        return []

    # 🔥 remove duplicates
    all_props = dedupe_props(all_props)

    print(f"📊 TOTAL PROPS COMBINED: {len(all_props)}")

    return all_props
