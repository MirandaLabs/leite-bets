from playwright.sync_api import sync_playwright

BETANO_URL = "https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=matchresult"

def get_session_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="pt-BR")
        page = context.new_page()

        page.goto(BETANO_URL, timeout=60000)
        page.wait_for_timeout(5000)

        cookies = context.cookies()
        headers = page.evaluate("() => Object.assign({}, window.navigator)")

        browser.close()

    return cookies
