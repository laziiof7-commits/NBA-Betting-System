# --------------------------------------------------
# 🔥 LINE ENGINE (BEST LINE + CLV)
# --------------------------------------------------

from collections import defaultdict

# ---------------- GROUP PROPS ----------------

def group_props(all_props):

    grouped = defaultdict(list)

    for p in all_props:
        key = f"{p['player']}-{p['stat']}"
        grouped[key].append(p)

    return grouped

# ---------------- BEST LINE ----------------

def get_best_lines(grouped):

    best = []

    for key, props in grouped.items():

        # sort by line
        props_sorted = sorted(props, key=lambda x: x["line"])

        best_over = props_sorted[0]     # lowest line
        best_under = props_sorted[-1]   # highest line

        best.append({
            "player": best_over["player"],
            "stat": best_over["stat"],
            "best_over_line": best_over["line"],
            "best_under_line": best_under["line"],
            "books": [p.get("book", "unknown") for p in props]
        })

    return best

# ---------------- CLV TRACKER ----------------

LAST_LINES = {}

def track_clv(player, stat, current_line):

    key = f"{player}-{stat}"

    prev = LAST_LINES.get(key)

    LAST_LINES[key] = current_line

    if prev is None:
        return 0

    return round(current_line - prev, 2)