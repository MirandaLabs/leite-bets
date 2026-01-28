"""
Workflow to collect Esportes da Sorte odds and send to API.
"""
import logging
from scrapers.base.esportesdasorte.collector import collect
from scrapers.shared.sender import send_odds_to_api

logger = logging.getLogger(__name__)


def run():
    """
    Main workflow:
    1. Collect odds from Esportes da Sorte
    2. Send collected data to external API
    
    Returns:
        list: Collected odds data (for backward compatibility with API response)
    """
    # Collect odds from Esportes da Sorte
    logger.info("Starting Esportes da Sorte odds collection")
    odds_data = collect()
    
    if not odds_data:
        logger.warning("No odds collected from Esportes da Sorte")
        return []
    
    logger.info(f"Collected {len(odds_data)} odds from Esportes da Sorte")
    
    # Send to external API
    success = send_odds_to_api(odds_data)
    
    if success:
        logger.info("Successfully sent Esportes da Sorte odds to API")
    else:
        logger.error("Failed to send Esportes da Sorte odds to API")
    
    # Return data for the API response
    return odds_data


if __name__ == "__main__":
    # Standalone execution
    from scrapers.base.esportesdasorte.app import main
    main()
