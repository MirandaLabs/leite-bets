# app/scrapers/bet365/parser.py

from typing import List, Dict, Any


def parse_futebol_events(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    events = payload.get("events", [])
    parsed = []

    for event in events:
        # FILTRO PREGAME
        if event.get("isLive"):
            continue

        parsed.append({
            "event_id": event.get("id"),
            "league": event.get("competitionName"),
            "home": event.get("homeName"),
            "away": event.get("awayName"),
            "start_time": event.get("startTime"),
            "markets": event.get("markets", []),
        })

    return parsed
