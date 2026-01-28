from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.base.betano.parser import parse_matchresult
from scrapers.shared.errors import ScraperError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BETANO_URL = "https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=doublechance"


def collect():
    """Collect match odds from Betano using Playwright."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = browser.new_context(
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            logger.info(f"Opening Betano URL: {BETANO_URL}")
            page.goto(BETANO_URL, timeout=60000, wait_until="domcontentloaded")
            
            # Wait a bit for dynamic content to load
            page.wait_for_timeout(5000)
            
            # Get the HTML content
            html = page.content()
            
            logger.info(f"HTML retrieved ({len(html)} bytes), parsing matches...")
            matches = parse_matchresult(html)
            
            logger.info(f"Found {len(matches)} matches")
            return matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Betano: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Betano: {str(e)}")
        finally:
            browser.close()

