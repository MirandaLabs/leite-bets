"""
Workflow to collect Superbet odds and send to API.
"""
import logging
import sys
from pathlib import Path
from scrapers.base.superbet.collector import collect
from scrapers.shared.sender import send_odds_to_api

logger = logging.getLogger(__name__)


def run():
    """
    Main workflow:
    1. Collect odds from Superbet
    2. Send collected data to external API
    
    Returns:
        list: Collected odds data (for backward compatibility with API response)
    """
    # Collect odds from Superbet
    logger.info("Starting Superbet odds collection")
    odds_data = collect()
    
    if not odds_data:
        logger.warning("No odds collected from Superbet")
        return []
    
    logger.info(f"Collected {len(odds_data)} odds from Superbet")
    
    # Send to external API
    success = send_odds_to_api(odds_data)
    
    if success:
        logger.info("Successfully sent Superbet odds to API")
    else:
        logger.error("Failed to send Superbet odds to API")
    
    # Return data for the API response
    return odds_data


if __name__ == "__main__":
    # Standalone execution
    from scrapers.base.superbet.app import main
    main()
