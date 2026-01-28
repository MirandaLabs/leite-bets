from playwright.sync_api import sync_playwright, TimeoutError
import logging

logger = logging.getLogger(__name__)

BET365_URL = "https://www.bet365.bet.br/"

class Bet365CollectorError(Exception):
    pass


def collect_futebol_1x2(max_items=None):
    """Collect 1X2 offers. If `max_items` is set, stop after collecting that many items."""
    collected = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        def handle_response(response):
            url = response.url.lower()

            if "offersapi" not in url:
                return

            try:
                data = response.json()
            except Exception:
                return

            # estrutura muda bastante, então defensivo
            offers = data.get("offers") or data.get("results") or []

            for offer in offers:
                market = offer.get("marketName") or offer.get("market")

                if market != "1X2":
                    continue

                event = offer.get("eventName") or offer.get("name")

                selections = offer.get("selections", [])
                odds = {}

                for sel in selections:
                    name = sel.get("name", "").lower()
                    price = sel.get("price")

                    if not price:
                        continue

                    if "home" in name or name == "1":
                        odds["home"] = price
                    elif "draw" in name or name == "x":
                        odds["draw"] = price
                    elif "away" in name or name == "2":
                        odds["away"] = price

                if odds:
                    collected.append({
                        "event": event,
                        "market": "1X2",
                        "odds": odds
                    })

                    # If we've collected enough, close the page to stop further requests
                    try:
                        if max_items and len(collected) >= int(max_items):
                            page.close()
                    except Exception:
                        pass

        page.on("response", handle_response)

        try:
            logger.info("Abrindo bet365...")
            page.goto(BET365_URL, timeout=60000)

            # espera tráfego acontecer
            page.wait_for_timeout(15000)

        except TimeoutError as e:
            raise Bet365CollectorError("Timeout ao carregar bet365") from e
        finally:
            browser.close()

    return collected
