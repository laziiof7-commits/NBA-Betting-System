# --------------------------------------------------
# 🔗 LINE ENGINE (UNIFY + BEST LINE)
# --------------------------------------------------

def group_lines(raw):

    grouped = {}

    for p in raw:

        key = f"{p.get('game')}-{p.get('stat')}"

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(p)

    return grouped


def get_best_lines(grouped):

    best = []

    for key, lines in grouped.items():

        # BEST LINE = most favorable to bettor
        if "spread" in key:
            best_line = max(lines, key=lambda x: x["line"])
        else:
            best_line = max(lines, key=lambda x: x["line"])

        best.append(best_line)

    return best
