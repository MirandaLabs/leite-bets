from bs4 import BeautifulSoup
from scrapers.base.betano.selectors import (
    EVENT_ROW,
    EVENT_NAME,
    ODDS_SELECTION,
    SELECTION_NAME,
    ODDS_VALUE
)
from scrapers.shared.models.odds import Odds, Event, Market, Selection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def parse_matchresult(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    matches = []
    
    events = soup.select(EVENT_ROW)
    logger.info(f"Found {len(events)} events with selector '{EVENT_ROW}'")

    for event in events:
        # Get event name (teams) - there are usually 2 spans for home/away team names
        event_name_elems = event.select(EVENT_NAME)
        logger.info(f"Event {events.index(event)+1}: Found {len(event_name_elems)} name elements with selector '{EVENT_NAME}'")
        
        if len(event_name_elems) < 2:
            logger.debug(f"Skipping event: need at least 2 team names, found {len(event_name_elems)}")
            continue
            
        # Combine team names (Home vs Away)
        event_name = f"{event_name_elems[0].get_text(strip=True)} vs {event_name_elems[1].get_text(strip=True)}"
        
        # Get all odds selections
        selections_elems = event.select(ODDS_SELECTION)
        
        if len(selections_elems) < 3:
            logger.debug(f"Skipping event '{event_name}': found only {len(selections_elems)} selections")
            continue
        
        # Parse selections (expecting 1X, 12, X2 for Double Chance)
        selections = []
        
        for sel_elem in selections_elems[:3]:  # Take only first 3 (1X, 12, X2)
            name_elem = sel_elem.select_one(SELECTION_NAME)
            odd_elem = sel_elem.select_one(ODDS_VALUE)
            
            if not name_elem or not odd_elem:
                continue
                
            sel_name = name_elem.get_text(strip=True)
            sel_odd_text = odd_elem.get_text(strip=True)
            
            try:
                sel_odd = float(sel_odd_text)
                
                # Map selection names for Double Chance
                if sel_name == "1X":
                    key = "1X"
                    display_name = "Home or Draw"
                elif sel_name == "12":
                    key = "12"
                    display_name = "Home or Away"
                elif sel_name == "X2":
                    key = "X2"
                    display_name = "Draw or Away"
                else:
                    continue
                
                selections.append(Selection(key=key, name=display_name, odd=sel_odd))
                
            except (ValueError, AttributeError) as e:
                logger.debug(f"Failed to parse odd value: {sel_odd_text}, error: {e}")
                continue
        
        if len(selections) != 3:
            logger.debug(f"Skipping event '\''{event_name}'\'': incomplete selections (found {len(selections)})")
            continue

        # Create Odds object
        matches.append(
            Odds(
                source="betano",
                sport="football",
                competition="brasileirao-serie-a",
                event=Event(
                    id=f"betano_{event_name}".replace(" ", "_").lower(),
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

    logger.info(f"Successfully parsed {len(matches)} matches")
    return matches
