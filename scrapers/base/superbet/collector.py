from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.base.superbet.parser import parse_matchresult_from_main_page
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPERBET_URL = "https://superbet.bet.br/apostas/futebol/brasil/brasileiro-serie-a/todos?cpi=4ivzYkpyZ0KYH5vHOJ6qVP&ct=m"


def collect():
    """Collect match odds from Superbet using Playwright with proxy rotation.
    
    Note: This collects only data available on the main page without navigating to individual events.
    Superbet's double chance odds may not be visible on the main listing page.
    """
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="superbet")
        page = context.new_page()

        try:
            logger.info(f"Opening Superbet URL: {SUPERBET_URL}")
            page.goto(SUPERBET_URL, timeout=60000, wait_until="domcontentloaded")
            
            # Try to close cookie consent popup if it exists
            try:
                logger.info("Checking for cookie consent popup...")
                accept_button = page.wait_for_selector(
                    "button#onetrust-accept-btn-handler",
                    timeout=5000,
                    state="visible"
                )
                if accept_button:
                    logger.info("Closing cookie consent popup...")
                    accept_button.click()
                    page.wait_for_timeout(2000)
            except Exception as e:
                logger.info(f"No cookie popup found or already closed: {str(e)}")
            
            # Wait for event cards to load
            logger.info("Waiting for event cards to load...")
            page.wait_for_selector("div.event-card.e2e-event-row", timeout=30000)
            
            # Wait a bit more for all content to render
            page.wait_for_timeout(3000)
            
            # Get the HTML content
            html = page.content()
            
            logger.info(f"HTML retrieved ({len(html)} bytes), parsing matches...")
            matches = parse_matchresult_from_main_page(html)
            
            logger.info(f"Total matches collected: {len(matches)}")
            return matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Superbet: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Superbet: {str(e)}")
        finally:
            browser.close()
