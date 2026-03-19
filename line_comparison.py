# --------------------------------------------------
# 🔥 LINE COMPARISON ENGINE (REAL EDGE DETECTION)
# --------------------------------------------------

def find_edges(dk_props, pp_props):

    edges = []

    # Map PrizePicks
    pp_map = {
        (p["player"], p["stat"]): p["line"]
        for p in pp_props
    }

    for dk in dk_props:

        key = (dk["player"], dk["stat"])

        if key not in pp_map:
            continue

        dk_line = dk["line"]
        pp_line = pp_map[key]

        edge = pp_line - dk_line

        # 🔥 EDGE THRESHOLD
        if abs(edge) >= 1.5:

            edges.append({
                "player": dk["player"],
                "stat": dk["stat"],
                "dk_line": dk_line,
                "pp_line": pp_line,
                "edge": round(edge, 2),
                "best_bet": "OVER" if edge > 0 else "UNDER"
            })

    return edges