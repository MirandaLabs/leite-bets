from playwright.sync_api import sync_playwright

def get_browser_context(playwright, user_data_dir="storage/browser"):
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ]
    )
    context = browser.new_context(
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    viewport={"width": 1366, "height": 768},
    locale="pt-BR",
    timezone_id="America/Sao_Paulo"

    )

    return browser, context
