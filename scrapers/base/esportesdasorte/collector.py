from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.base.esportesdasorte.parser import parse_double_chance
from scrapers.shared.errors import ScraperError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ESPORTESDASORTE_URL = "https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026"


def collect():
    """Collect double chance odds from Esportes da Sorte using Playwright."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # Must be True for Docker environment
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
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
            
            # Process each match (limit to first 10 for safety)
            for idx, match_elem in enumerate(match_elements[:10]):
                try:
                    # Get team names before clicking
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
                    
                    logger.info(f"Processing match {idx+1}: {team1} vs {team2}")
                    
                    # Click on the match element using JavaScript to bypass overlay issues
                    try:
                        page.evaluate("(element) => element.click()", match_elem)
                    except:
                        # Fallback to regular click
                        match_elem.click()
                    
                    # Wait for the match page to load
                    page.wait_for_timeout(3000)
                    
                    # Wait for bet buttons to appear
                    try:
                        page.wait_for_selector("div.flex-container.bet-type-btn-group", timeout=10000)
                    except:
                        logger.warning(f"No bet groups found for {team1} vs {team2}")
                        page.go_back()
                        page.wait_for_timeout(2000)
                        continue
                    
                    # Get the HTML content of the match page
                    html = page.content()
                    
                    # Parse the match data
                    matches = parse_double_chance(html, team1, team2)
                    
                    if matches:
                        all_matches.extend(matches)
                        logger.info(f"Successfully extracted double chance odds for {team1} vs {team2}")
                    else:
                        logger.warning(f"No double chance odds found for {team1} vs {team2}")
                    
                    # Go back to the main page
                    page.go_back()
                    page.wait_for_selector("div.element.flex-item.match", timeout=10000)
                    page.wait_for_timeout(2000)
                    
                    # Re-query match elements as DOM might have changed
                    match_elements = page.query_selector_all("div.element.flex-item.match")
                    
                except Exception as e:
                    logger.error(f"Error processing match {idx+1}: {str(e)}")
                    # Try to go back to main page
                    try:
                        page.go_back()
                        page.wait_for_timeout(2000)
                    except:
                        pass
                    continue
            
            logger.info(f"Total matches collected: {len(all_matches)}")
            return all_matches

        except TimeoutError as e:
            raise ScraperError(f"Timeout loading Esportes da Sorte: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Error collecting from Esportes da Sorte: {str(e)}")
        finally:
            browser.close()
