RESULTS = []

def record_result(prop, result, stake):

    profit = 0

    if result == "win":
        profit = stake * 0.91
    elif result == "loss":
        profit = -stake

    RESULTS.append({
        "player": prop["player"],
        "stat": prop["stat"],
        "result": result,
        "profit": profit
    })


def get_roi():

    total = sum(r["profit"] for r in RESULTS)
    bets = len(RESULTS)

    if bets == 0:
        return 0

    return round(total / bets, 2)