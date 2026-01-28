"""  
Sender module for posting scraped odds data to external API.
"""
import requests
import logging
import json
import os
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Get API URL from environment variable or use default
DEFAULT_API_URL = os.getenv("API_URL", "http://api:8000/api/odds/scraper")


def _serialize_datetime(obj):
    """Helper function to serialize datetime objects to ISO format strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def send_odds_to_api(odds_data: List[Dict[str, Any]], api_url: str = None) -> bool:
    """
    Send scraped odds data to the external API endpoint.
    
    Args:
        odds_data: List of odds dictionaries from scrapers
        api_url: Target API endpoint URL (default: from env var API_URL or http://api:8000/api/odds/scraper)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if api_url is None:
        api_url = DEFAULT_API_URL
    
    if not odds_data:
        logger.warning("No odds data to send")
        return False
    
    try:
        logger.info(f"Sending {len(odds_data)} odds records to {api_url}")
        
        # Wrap the data in the expected payload format
        payload = {"data": odds_data}
        
        # Serialize the data to JSON with datetime handling
        json_data = json.dumps(payload, default=_serialize_datetime)
        
        response = requests.post(
            api_url,
            data=json_data,
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


# Alias for backward compatibility
send_to_api = send_odds_to_api
