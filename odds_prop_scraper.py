from playwright.sync_api import sync_playwright
import time

def get_odds_props():

    props = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 🔥 HIT REAL SITE (DK example)
            page.goto("https://sportsbook.draftkings.com/leagues/basketball/nba", timeout=60000)

            time.sleep(5)

            content = page.content()

            # 🔥 VERY BASIC PARSE (we'll upgrade next)
            if "Points" in content:
                print("✅ Page loaded successfully")

                # fake extraction placeholder
                props.append({
                    "player": "test player",
                    "stat": "points",
                    "line": 20.5,
                    "book": "draftkings"
                })

            browser.close()

    except Exception as e:
        print("❌ Playwright error:", e)

    print(f"📊 PLAYWRIGHT PROPS: {len(props)}")
    return props
