from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.base.esportesdasorte.parser import parse_double_chance
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ESPORTESDASORTE_URL = "https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026"


def collect():
    """Collect double chance odds from Esportes da Sorte using Playwright with proxy rotation."""
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="esportesdasorte")
        page = context.new_page()

        try:
            logger.info(f"Opening Esportes da Sorte URL: {ESPORTESDASORTE_URL}")
            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
            
            # Try to close any modal overlays
            try:
                logger.info("Checking for modal overlays...")
                page.wait_for_timeout(2000)
                
                # Try to close modal by clicking overlay or close button
                modal_overlay = page.query_selector("div.modal-overlay")
                if modal_overlay:
                    logger.info("Found modal overlay, attempting to close...")
                    # Try to find and click close button
                    close_buttons = page.query_selector_all("button.close, button.modal-close, i.close")
                    if close_buttons:
                        close_buttons[0].click()
                        page.wait_for_timeout(1000)
                    else:
                        # Click on overlay to close
                        modal_overlay.click()
                        page.wait_for_timeout(1000)
            except Exception as e:
                logger.info(f"No modal to close or already closed: {str(e)}")
            
            # Wait for match elements to load
            logger.info("Waiting for match elements to load...")
            page.wait_for_selector("div.element.flex-item.match", timeout=30000)
            
            # Wait for content to render
            page.wait_for_timeout(3000)
            
            # Save HTML for debugging
            html_content = page.content()
            import os
            os.makedirs("storage/debug", exist_ok=True)
            with open("storage/debug/esportesdasorte.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("Saved HTML to storage/debug/esportesdasorte.html for inspection")
            
            # Get all match elements
            match_elements = page.query_selector_all("div.element.flex-item.match")
            logger.info(f"Found {len(match_elements)} matches on main page")
            
            all_matches = []
            successful_collections = 0
            
            # Process each match (limit to first 10 for safety)
            for idx in range(min(10, len(match_elements))):
                try:
                    # Reload the main page to get fresh DOM elements
                    if idx > 0:
                        logger.info(f"Reloading main page for match {idx+1}...")
                        page.goto(ESPORTESDASORTE_URL, timeout=30000, wait_until="domcontentloaded")
                        page.wait_for_selector("div.element.flex-item.match", timeout=15000)
                        page.wait_for_timeout(2000)
                    
                    # Re-query match elements with fresh DOM
                    match_elements = page.query_selector_all("div.element.flex-item.match")
                    
                    if idx >= len(match_elements):
                        logger.warning(f"Match {idx+1} not found after reload, stopping")
                        break
                    
                    match_elem = match_elements[idx]
                    
                    # Get team names
                    team_links = match_elem.query_selector_all("a.team-name")
                    
                    if len(team_links) < 2:
                        logger.warning(f"Match {idx+1}: Could not find 2 team names, skipping")
                        continue
                    
                    # Extract team names
                    team1_text = team_links[0].query_selector("div.text.truncate")
                    team2_text = team_links[1].query_selector("div.text.truncate")
                    
                    if not team1_text or not team2_text:
                        logger.warning(f"Match {idx+1}: Could not extract team text, skipping")
                        continue
                    
                    team1 = team1_text.inner_text().strip()
                    team2 = team2_text.inner_text().strip()
                    
                    logger.info(f"Processing match {idx+1}/{min(10, len(match_elements))}: {team1} vs {team2}")
                    
                    # Store current URL to detect navigation
                    current_url = page.url
                    
                    # Click on the first team link (more reliable than clicking on container)
                    try:
                        team_links[0].click(timeout=5000)
                    except Exception as click_error:
                        logger.warning(f"Failed to click team link: {click_error}, trying JavaScript click")
                        page.evaluate("(element) => element.click()", team_links[0])
                    
                    # Wait for URL to change or content to load
                    try:
                        page.wait_for_url(lambda url: url != current_url, timeout=5000)
                    except:
                        # URL didn't change, wait for bet groups anyway
                        pass
                    
                    # Wait for the match page to load
                    page.wait_for_timeout(2000)
                    
                    # Wait for bet buttons to appear
                    try:
                        page.wait_for_selector("div.flex-container.bet-type-btn-group", timeout=10000)
                        page.wait_for_timeout(1000)
                    except:
                        logger.warning(f"No bet groups found for {team1} vs {team2}")
                        continue
                    
                    # Get the HTML content of the match page
                    html = page.content()
                    
                    # Parse the match data
                    matches = parse_double_chance(html, team1, team2)
                    
                    if matches:
                        all_matches.extend(matches)
                        successful_collections += 1
                        logger.info(f"✓ Successfully extracted double chance odds for {team1} vs {team2} ({successful_collections} collected)")
                    else:
                        logger.warning(f"No double chance odds found for {team1} vs {team2}")
                    
                except Exception as e:
                    logger.error(f"Error processing match {idx+1}: {str(e)}")
                    continue
            
            logger.info(f"Total matches collected: {len(all_matches)} (attempted {min(10, len(match_elements))})")
            return all_matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Esportes da Sorte: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Esportes da Sorte: {str(e)}")
        finally:
            browser.close()
