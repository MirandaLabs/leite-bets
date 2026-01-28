"""
Esportes da Sorte scraper entry point
"""
from scrapers.base.esportesdasorte.collector import collect
from scrapers.shared.sender import send_odds_to_api
from scrapers.shared.logger import setup_logger
import sys

logger = setup_logger("esportesdasorte")


def main():
    """Main entry point for Esportes da Sorte scraper."""
    try:
        logger.info("Starting Esportes da Sorte scraper...")
        
        # Collect odds
        matches = collect()
        
        if not matches:
            logger.warning("No matches collected")
            return
        
        logger.info(f"Collected {len(matches)} matches")
        
        # Send to API
        logger.info("Sending data to API...")
        success = send_odds_to_api(matches)
        
        if success:
            logger.info(f"Successfully sent {len(matches)} matches to API")
        else:
            logger.error("Failed to send data to API")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in Esportes da Sorte scraper: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
