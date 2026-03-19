# --------------------------------------------------
# 🔥 ODDS PROP SCRAPER (SAFE MODE)
# --------------------------------------------------

# ⚠️ Odds API does NOT support player props reliably
# So we disable it to prevent 422 spam

def get_odds_props():
    print("⚠️ Odds API player props disabled (unsupported)")
    return []
