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
            
            # Wait for network to be idle (JavaScript loaded)
            page.goto(BETANO_URL, timeout=60000, wait_until="networkidle")
            
            logger.info(f"Page loaded, waiting for content to render...")
            
            # Wait for the event container to appear (or timeout after 15s)
            try:
                page.wait_for_selector("div.tw-flex.tw-w-full.tw-flex-row.tw-items-start", timeout=15000)
                logger.info("✅ Event container found!")
            except TimeoutError:
                logger.warning("⚠️ Event container not found, trying alternative selectors...")
                # Try waiting for any Betano content
                try:
                    page.wait_for_selector("div[class*='tw-']", timeout=10000)
                except TimeoutError:
                    logger.error("❌ No Betano content loaded - site may be blocking or page structure changed")
            
            # Additional wait for dynamic content
            page.wait_for_timeout(3000)
            
            # Get the HTML content
            html = page.content()
            title = page.title()
            
            logger.info(f"HTML retrieved ({len(html)} bytes), title: {title}")
            
            # Check if we got the splash screen instead of real content
            if "splash" in title.lower() or len(html) < 10000:
                logger.error(f"⚠️ Got splash screen or incomplete HTML!")
                logger.error(f"Title: {title}")
                logger.error(f"HTML size: {len(html)} bytes")
                return []
            
            matches = parse_matchresult(html)
            
            logger.info(f"Found {len(matches)} matches")
            return matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Betano: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Betano: {str(e)}")
        finally:
            browser.close()

