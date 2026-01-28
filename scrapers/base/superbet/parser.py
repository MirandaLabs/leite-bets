from bs4 import BeautifulSoup
from scrapers.base.superbet.selectors import (
    EVENT_CARD,
    EVENT_TEAM1_NAME,
    EVENT_TEAM2_NAME,
    MARKET_CONTAINER,
    MARKET_ODD,
    ODD_NAME,
    ODD_VALUE
)
from scrapers.shared.models.odds import Odds, Event, Market, Selection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def parse_matchresult_from_main_page(html: str) -> list:
    """Parse 1X2 odds from Superbet main page HTML.
    
    Args:
        html: HTML content of the main listing page
    
    Returns:
        List of Odds objects containing 1X2 selections from the main page
    """
    soup = BeautifulSoup(html, "lxml")
    matches = []
    
    # Find all event cards
    event_cards = soup.select(EVENT_CARD)
    logger.info(f"Found {len(event_cards)} event cards")
    
    for idx, card in enumerate(event_cards, 1):
        try:
            # Get team names
            team1_elem = card.select_one(EVENT_TEAM1_NAME)
            team2_elem = card.select_one(EVENT_TEAM2_NAME)
            
            if not team1_elem or not team2_elem:
                logger.warning(f"Event {idx}: Could not find team names, skipping")
                continue
            
            team1 = team1_elem.get_text(strip=True)
            team2 = team2_elem.get_text(strip=True)
            event_name = f"{team1} vs {team2}"
            
            # Find odds in the card - usually showing 1X2 on main page
            odd_buttons = card.select("button.odd-button")
            
            if len(odd_buttons) < 3:
                logger.warning(f"Event {event_name}: Found only {len(odd_buttons)} odds, need 3 for 1X2")
                continue
            
            selections = []
            expected_keys = ["1", "X", "2"]
            
            for i, button in enumerate(odd_buttons[:3]):
                name_elem = button.select_one(ODD_NAME)
                value_elem = button.select_one(ODD_VALUE)
                
                if not name_elem or not value_elem:
                    continue
                
                odd_name = name_elem.get_text(strip=True)
                odd_value_text = value_elem.get_text(strip=True)
                
                try:
                    odd_value = float(odd_value_text)
                    
                    # Map based on position (1st=Home, 2nd=Draw, 3rd=Away)
                    if i == 0:
                        key = "1"
                        display_name = "Home"
                    elif i == 1:
                        key = "X"
                        display_name = "Draw"
                    elif i == 2:
                        key = "2"
                        display_name = "Away"
                    else:
                        continue
                    
                    selections.append(Selection(key=key, name=display_name, odd=odd_value))
                    logger.debug(f"  {key} ({display_name}): {odd_value}")
                    
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse odd: {odd_value_text}, error: {e}")
                    continue
            
            if len(selections) == 3:
                matches.append(
                    Odds(
                        source="superbet",
                        sport="football",
                        competition="brasileirao-serie-a",
                        event=Event(
                            id=f"superbet_{event_name}".replace(" ", "_").lower(),
                            name=event_name,
                            start_time=None,
                            is_live=False
                        ),
                        market=Market(
                            type="1X2",
                            name="Match Result",
                            selections=selections
                        ),
                        collected_at=datetime.utcnow()
                    ).model_dump()
                )
                logger.info(f"Successfully parsed {event_name}")
            else:
                logger.warning(f"Incomplete selections for {event_name}: found {len(selections)}")
                
        except Exception as e:
            logger.error(f"Error parsing event card {idx}: {str(e)}")
            continue
    
    return matches


def parse_matchresult(html: str, team1: str, team2: str) -> list:
    """Parse double chance odds from Superbet event page HTML.
    
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
    
    # Find the market container with double chance odds
    market_containers = soup.select(MARKET_CONTAINER)
    logger.info(f"Found {len(market_containers)} market containers")
    
    # Look for the container with double chance odds
    # The structure has 3 buttons: "1 ou Empate", "Empate ou 2", "1 ou 2"
    for market in market_containers:
        market_odds = market.select(MARKET_ODD)
        
        # Double chance should have exactly 3 selections
        if len(market_odds) != 3:
            continue
        
        # Check if this is the double chance market by examining the names
        odd_names = []
        for odd_elem in market_odds:
            name_elem = odd_elem.select_one(ODD_NAME)
            if name_elem:
                odd_names.append(name_elem.get_text(strip=True))
        
        # Check if we have the expected double chance options
        expected_names = ["1 ou Empate", "Empate ou 2", "1 ou 2"]
        if not all(name in odd_names for name in expected_names):
            continue
        
        logger.info(f"Found double chance market for {event_name}")
        
        # Parse the selections
        selections = []
        
        for odd_elem in market_odds:
            name_elem = odd_elem.select_one(ODD_NAME)
            value_elem = odd_elem.select_one(ODD_VALUE)
            
            if not name_elem or not value_elem:
                logger.warning("Missing name or value element in odd")
                continue
            
            sel_name = name_elem.get_text(strip=True)
            sel_odd_text = value_elem.get_text(strip=True)
            
            try:
                sel_odd = float(sel_odd_text)
                
                # Map Superbet names to standard format
                if sel_name == "1 ou Empate":
                    key = "1X"
                    display_name = "Home or Draw"
                elif sel_name == "1 ou 2":
                    key = "12"
                    display_name = "Home or Away"
                elif sel_name == "Empate ou 2":
                    key = "X2"
                    display_name = "Draw or Away"
                else:
                    logger.warning(f"Unknown selection name: {sel_name}")
                    continue
                
                selections.append(Selection(key=key, name=display_name, odd=sel_odd))
                logger.info(f"  {key} ({display_name}): {sel_odd}")
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse odd value: {sel_odd_text}, error: {e}")
                continue
        
        # Only create the match if we have all 3 selections
        if len(selections) == 3:
            matches.append(
                Odds(
                    source="superbet",
                    sport="football",
                    competition="brasileirao-serie-a",
                    event=Event(
                        id=f"superbet_{event_name}".replace(" ", "_").lower(),
                        name=event_name,
                        start_time=None,
                        is_live=False
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
