from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.base.betano.parser import parse_matchresult
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BETANO_URL = "https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=doublechance"


def collect():
    """Collect match odds from Betano using Playwright with proxy rotation."""
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="betano")
        page = context.new_page()

        try:
            logger.info(f"Opening Betano URL: {BETANO_URL}")
            page.goto(BETANO_URL, timeout=60000, wait_until="domcontentloaded")
            
            # Wait a bit for dynamic content to load
            page.wait_for_timeout(5000)
            
            # Get the HTML content
            html = page.content()
            
            logger.info(f"HTML retrieved ({len(html)} bytes), parsing matches...")
            
            # Debug: Check if we're getting blocked
            if len(html) < 5000:
                logger.warning(f"⚠️ HTML muito pequeno ({len(html)} bytes) - possível bloqueio!")
                logger.warning(f"Primeiros 500 caracteres: {html[:500]}")
                logger.warning(f"Title da página: {page.title()}")
            
            matches = parse_matchresult(html)
            
            logger.info(f"Found {len(matches)} matches")
            return matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Betano: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Betano: {str(e)}")
        finally:
            browser.close()

