from playwright.sync_api import sync_playwright, TimeoutError
import logging
import time
import random
from scrapers.base.betano.parser import parse_matchresult
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

from playwright_stealth import stealth_sync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BETANO_URL = "https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=doublechance"


def collect():
    """Collect match odds from Betano using Playwright with proxy rotation."""
    browser, context = get_browser_context(p, scraper_name="betano")
    page = context.new_page()
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="betano")
        page = context.new_page()
        stealth_sync(page)

        try:
            logger.info(f"Opening Betano URL: {BETANO_URL}")
            
            # Random delay to simulate human behavior (1-3 seconds)
            delay = random.uniform(1.0, 3.0)
            logger.info(f"⏱️  Aguardando {delay:.1f}s (comportamento humano)")
            time.sleep(delay)
            
            # Initial navigation
            response = page.goto(BETANO_URL, timeout=60000, wait_until="networkidle")
            logger.info(f"Initial load complete, status: {response.status}")
            
            # Check for blocking
            if response.status == 403:
                logger.error("❌ Betano returned 403 Forbidden - proxy detectado!")
                logger.error("💡 Proxies datacenter são facilmente detectados por sites de apostas")
                logger.error("💡 Considere: proxies residenciais ou aguardar rotação automática")
                return []
            elif response.status >= 400:
                logger.error(f"❌ Betano returned error status: {response.status}")
                return []
            
            # Check if we got the splash screen
            title = page.title()
            if "splash" in title.lower():
                logger.warning("⚠️ Got splash screen, waiting for redirect...")
                
                # Wait for content to appear (max 20 seconds)
                try:
                    page.wait_for_function(
                        "document.querySelector('div.tw-flex') !== null",
                        timeout=20000
                    )
                    logger.info("✅ Content appeared after splash!")
                except TimeoutError:
                    logger.error("❌ Splash screen timeout - no content loaded")
                    return []
            
            # Wait for content to load
            logger.info(f"Waiting for event container...")
            try:
                page.wait_for_selector("div.tw-flex.tw-w-full.tw-flex-row.tw-items-start", timeout=15000)
                logger.info("✅ Event container found!")
            except TimeoutError:
                logger.warning("⚠️ Event container not found with primary selector")
                
                # Try alternative - wait for any event-like structure
                try:
                    page.wait_for_selector("div[class*='event'], div[class*='match']", timeout=10000)
                    logger.info("✅ Found alternative event selector")
                except TimeoutError:
                    logger.error("❌ No event content found - page may not have matches or is blocked")
            
            # Final wait for any dynamic updates
            page.wait_for_timeout(2000)
            
            # Get the HTML content
            html = page.content()
            title = page.title()
            
            logger.info(f"Final HTML: {len(html)} bytes, title: '{title}'")
            
            # Validate we have real content
            if "splash" in title.lower() or len(html) < 10000:
                logger.error(f"❌ Still on splash screen or incomplete page!")
                logger.error(f"Current URL: {page.url}")
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

