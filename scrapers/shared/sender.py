"""
Sender module for posting scraped odds data to external API.
"""
import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def send_odds_to_api(odds_data: List[Dict[str, Any]], api_url: str = "http://localhost:8000/api/odds/scraper") -> bool:
    """
    Send scraped odds data to the external API endpoint.
    
    Args:
        odds_data: List of odds dictionaries from scrapers
        api_url: Target API endpoint URL (default: http://localhost:8000/api/odds/scraper)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not odds_data:
        logger.warning("No odds data to send")
        return False
    
    try:
        logger.info(f"Sending {len(odds_data)} odds records to {api_url}")
        
        response = requests.post(
            api_url,
            json=odds_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        
        logger.info(f"Successfully sent {len(odds_data)} odds records. Status: {response.status_code}")
        return True
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while sending data to {api_url}")
        return False
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to {api_url}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}, body: {e.response.text}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error sending data: {e}")
        return False
