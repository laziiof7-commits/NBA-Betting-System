# --------------------------------------------------
# 📊 MULTI-BOOK PLAYER + GAME SCRAPER (REAL)
# --------------------------------------------------

from prizepicks_scraper import get_prizepicks_props
from draftkings_scraper import get_dk_props
from fanduel_scraper import get_fd_props

def normalize_name(name):
    return name.lower().replace(".", "").strip()

def get_odds_props():

    all_props = []

    # ---------------- PRIZEPICKS ----------------
    try:
        pp = get_prizepicks_props()
        for p in pp:
            all_props.append({
                "player": normalize_name(p["player"]),
                "stat": p["stat"],
                "line": p["line"],
                "book": "pp"
            })
    except Exception as e:
        print("❌ PP ERROR:", e)

    # ---------------- DRAFTKINGS ----------------
    try:
        dk = get_dk_props()
        for p in dk:
            all_props.append({
                "player": normalize_name(p["player"]),
                "stat": p["stat"],
                "line": p["line"],
                "book": "dk"
            })
    except Exception as e:
        print("❌ DK ERROR:", e)

    # ---------------- FANDUEL ----------------
    try:
        fd = get_fd_props()
        for p in fd:
            all_props.append({
                "player": normalize_name(p["player"]),
                "stat": p["stat"],
                "line": p["line"],
                "book": "fd"
            })
    except Exception as e:
        print("❌ FD ERROR:", e)

    # ---------------- GROUP + BEST LINE ----------------
    grouped = {}

    for p in all_props:

        key = f"{p['player']}-{p['stat']}"

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(p)

    best_lines = []

    for key, lines in grouped.items():

        # 🔥 BEST LINE = lowest for over, highest for under
        best = min(lines, key=lambda x: x["line"])

        best_lines.append({
            "player": best["player"],
            "stat": best["stat"],
            "line": best["line"],
            "books": [x["book"] for x in lines],
            "raw": lines
        })

    print(f"📊 UNIFIED PLAYER PROPS: {len(best_lines)}")

    return best_lines
