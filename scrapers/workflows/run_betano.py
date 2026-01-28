"""
Workflow to collect Betano odds and send to API.
"""
import logging
from scrapers.base.betano.collector import collect
from scrapers.shared.sender import send_odds_to_api

logger = logging.getLogger(__name__)


def run():
    """
    Main workflow:
    1. Collect odds from Betano
    2. Send collected data to external API
    
    Returns:
        dict: Summary of the operation
    """
    # Collect odds from Betano
    logger.info("Starting Betano odds collection")
    odds_data = collect()
    
    if not odds_data:
        logger.warning("No odds collected from Betano")
        return {
            "status": "no_data",
            "collected": 0,
            "sent": False
        }
    
    logger.info(f"Collected {len(odds_data)} odds from Betano")
    
    # Send to external API
    success = send_odds_to_api(odds_data)
    
    return {
        "status": "success" if success else "send_failed",
        "collected": len(odds_data),
        "sent": success
    }
