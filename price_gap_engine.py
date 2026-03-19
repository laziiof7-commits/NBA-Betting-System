# --------------------------------------------------
# 📊 CROSS-BOOK PRICE GAP ENGINE (ELITE SIGNAL)
# --------------------------------------------------

def detect_price_gaps(lines, threshold=1.5):

    gaps = []

    grouped = {}

    # ---------------- GROUP ----------------
    for p in lines:

        player = p.get("player")
        stat = p.get("stat")

        if not player or not stat:
            continue

        key = f"{player}-{stat}"

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(p)

    # ---------------- FIND GAPS ----------------
    for key, books in grouped.items():

        if len(books) < 2:
            continue

        try:
            highest = max(books, key=lambda x: x["line"])
            lowest = min(books, key=lambda x: x["line"])

            gap = highest["line"] - lowest["line"]

            if gap >= threshold:

                gaps.append({
                    "type": "price_gap",
                    "player": highest["player"],
                    "stat": highest["stat"],
                    "gap": round(gap, 2),

                    "best_line": lowest["line"],
                    "best_book": lowest.get("book"),

                    "worst_line": highest["line"],
                    "worst_book": highest.get("book"),

                    # 🔥 useful for your model
                    "confidence_boost": round(gap / 2, 2)
                })

        except Exception:
            continue

    return gaps