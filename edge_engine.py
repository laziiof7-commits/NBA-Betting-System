# --------------------------------------------------
# 🎯 EDGE ENGINE (TRUE +EV DETECTION)
# --------------------------------------------------

def calculate_edge(model_line, market_line):

    return round(model_line - market_line, 2)


def is_mispriced(edge, threshold=1.5):

    return abs(edge) >= threshold


def expected_value(prob, odds=1.91):

    return round((prob * (odds - 1)) - (1 - prob), 3)