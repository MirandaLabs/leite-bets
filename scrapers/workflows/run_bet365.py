# scrapers/workflows/run_bet365.py
"""
Workflow to collect Bet365 odds and send to API.
"""
import logging
from scrapers.base.bet365.collector import collect_double_chance
from scrapers.shared.sender import send_odds_to_api

logger = logging.getLogger(__name__)


def run(url=None):
    """
    Main workflow:
    1. Collect odds from Bet365
    2. Send collected data to external API
    
    Returns:
        list: Collected odds data (for backward compatibility with API response)
    """
    target_url = url or "https://www.bet365.bet.br/#/AC/B1/C1/D100/E40/"  # Default: Serie A
    
    # Collect odds from Bet365
    logger.info(f"Starting Bet365 odds collection from {target_url}")
    odds_data = collect_double_chance(target_url)
    
    if not odds_data:
        logger.warning("No odds collected from Bet365")
        return []
    
    logger.info(f"Collected {len(odds_data)} odds from Bet365")
    
    # Send to external API
    success = send_odds_to_api(odds_data)
    
    if success:
        logger.info("Successfully sent Bet365 odds to API")
    else:
        logger.error("Failed to send Bet365 odds to API")
    
    # Return data for the API response
    return odds_data