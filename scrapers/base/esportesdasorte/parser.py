from bs4 import BeautifulSoup
from scrapers.base.esportesdasorte.selectors import (
    BET_TYPE_GROUP,
    BET_BUTTON,
    BET_TEXT,
    BET_ODD
)
from scrapers.shared.models.odds import Odds, Event, Market, Selection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def parse_double_chance(html: str, team1: str, team2: str) -> list:
    """Parse double chance odds from Esportes da Sorte event page HTML.
    
    Args:
        html: HTML content of the event page
        team1: Name of the home team
        team2: Name of the away team
    
    Returns:
        List with a single Odds object containing double chance selections
    """
    soup = BeautifulSoup(html, "lxml")
    matches = []
    
    event_name = f"{team1} vs {team2}"
    
    # Find all bet type groups
    bet_groups = soup.select(BET_TYPE_GROUP)
    logger.info(f"Found {len(bet_groups)} bet type groups")
    
    # Look for the group with double chance odds
    for group in bet_groups:
        bet_buttons = group.select(BET_BUTTON)
        
        # Double chance should have exactly 3 selections
        if len(bet_buttons) != 3:
            continue
        
        # Check if this is the double chance market by examining the names
        bet_names = []
        for button in bet_buttons:
            text_elem = button.select_one(BET_TEXT)
            if text_elem:
                bet_names.append(text_elem.get_text(strip=True))
        
        # Check if we have the expected double chance options
        expected_names = ["Casa Ou Empate", "Casa Ou Fora", "Empate Ou Fora"]
        if not all(name in bet_names for name in expected_names):
            continue
        
        logger.info(f"Found double chance market for {event_name}")
        
        # Parse the selections
        selections = []
        
        for button in bet_buttons:
            text_elem = button.select_one(BET_TEXT)
            odd_elem = button.select_one(BET_ODD)
            
            if not text_elem or not odd_elem:
                logger.warning("Missing text or odd element in button")
                continue
            
            bet_name = text_elem.get_text(strip=True)
            odd_text = odd_elem.get_text(strip=True)
            
            try:
                odd_value = float(odd_text)
                
                # Map Esportes da Sorte names to standard format
                if bet_name == "Casa Ou Empate":
                    key = "1X"
                    display_name = "Home or Draw"
                elif bet_name == "Casa Ou Fora":
                    key = "12"
                    display_name = "Home or Away"
                elif bet_name == "Empate Ou Fora":
                    key = "X2"
                    display_name = "Draw or Away"
                else:
                    logger.warning(f"Unknown bet name: {bet_name}")
                    continue
                
                selections.append(Selection(key=key, name=display_name, odd=odd_value))
                logger.info(f"  {key} ({display_name}): {odd_value}")
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse odd value: {odd_text}, error: {e}")
                continue
        
        # Only create the match if we have all 3 selections
        if len(selections) == 3:
            matches.append(
                Odds(
                    source="esportesdasorte",
                    sport="football",
                    competition="brasileirao-serie-a",
                    event=Event(
                        id=f"esportesdasorte_{event_name}".replace(" ", "_").lower(),
                        name=event_name,
                        start_time=None,
                        status="upcoming"
                    ),
                    market=Market(
                        type="Double Chance",
                        name="Double Chance",
                        selections=selections
                    ),
                    collected_at=datetime.utcnow()
                ).model_dump()
            )
            break  # Found the double chance market, no need to continue
        else:
            logger.warning(f"Incomplete double chance selections for {event_name}: found {len(selections)}")
    
    if not matches:
        logger.warning(f"No double chance market found for {event_name}")
    
    return matches
