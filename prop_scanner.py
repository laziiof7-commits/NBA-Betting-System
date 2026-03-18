# --------------------------------------------------
# 🔥 ELITE PROP SCANNER (MULTI-SOURCE + ML + STEAM)
# --------------------------------------------------

# --------------------------------------------------
# SAFE IMPORTS
# --------------------------------------------------

try:
    from prizepicks_scraper import get_prizepicks_props
except:
    def get_prizepicks_props(): return []

try:
    from odds_prop_scraper import get_odds_props
except:
    def get_odds_props(): return []

try:
    from prop_model import evaluate_prop, is_good_prop, prop_bet_size
except:
    def evaluate_prop(**kwargs): return None
    def is_good_prop(x): return False
    def prop_bet_size(*args, **kwargs): return 0

try:
    from prop_tracker import log_prop
except:
    def log_prop(x): pass

try:
    from line_movement_tracker import update_line, get_movement, is_steam_move
except:
    def update_line(*args): pass
    def get_movement(*args): return 0
    def is_steam_move(*args): return False

try:
    from player_team_map import get_player_team
except:
    def get_player_team(x): return None


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MIN_EDGE = 2.5
MIN_PROB = 0.55


# --------------------------------------------------
# MERGE PROP SOURCES
# --------------------------------------------------

def merge_props():

    props = []

    try:
        pp = get_prizepicks_props()
        odds = get_odds_props()

        if isinstance(pp, list):
            props.extend(pp)

        if isinstance(odds, list):
            props.extend(odds)

    except Exception as e:
        print("❌ MERGE ERROR:", e)

    return props


# --------------------------------------------------
# SCAN PROPS
# --------------------------------------------------

def scan_props():

    raw_props = merge_props()

    if not raw_props:
        print("⚠️ No props found")
        return []

    results = []

    for p in raw_props:

        try:
            player = p.get("player")
            stat = p.get("stat")
            line = p.get("line")

            if not player or line is None:
                continue

            # -----------------------------
            # TEAM CONTEXT
            # -----------------------------
            team = get_player_team(player)
            opponent = None  # can improve later

            # -----------------------------
            # TRACK LINE MOVEMENT
            # -----------------------------
            update_line(player, stat, line)

            movement = get_movement(player, stat)
            steam = is_steam_move(player, stat)

            # -----------------------------
            # MODEL EVALUATION
            # -----------------------------
            result = evaluate_prop(
                player=player,
                stat=stat,
                line=line,
                team=team,
                opponent=opponent
            )

            if not result:
                continue

            # -----------------------------
            # ENHANCE WITH MARKET SIGNALS
            # -----------------------------
            result["movement"] = movement
            result["steam"] = steam

            # boost if market agrees
            if movement > 1:
                result["edge"] += 1.2

            if steam:
                result["confidence"] += 0.1

            # -----------------------------
            # FILTER (ELITE ONLY)
            # -----------------------------
            if (
                result["edge"] >= MIN_EDGE
                and result["probability"] >= MIN_PROB
                and is_good_prop(result)
            ):

                result["bet_size"] = prop_bet_size(result, base_size=10)

                # log it
                log_prop(result)

                results.append(result)

        except Exception as e:
            print("❌ PROP SCAN ERROR:", e)
            continue

    # --------------------------------------------------
    # SORT BEST PROPS
    # --------------------------------------------------

    results = sorted(
        results,
        key=lambda x: (x["confidence"], x["edge"]),
        reverse=True
    )

    return results


# --------------------------------------------------
# TOP PROPS
# --------------------------------------------------

def get_top_props(n=10):

    props = scan_props()

    return props[:n]