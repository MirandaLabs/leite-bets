from datetime import datetime

def build_odds_schema(
    source: str,
    sport: str,
    competition: str,
    event_name: str,
    market_type: str,
    selections: list
):
    return {
        "source": source,
        "sport": sport,
        "competition": competition,
        "event": {
            "id": None,
            "name": event_name,
            "start_time": None,
            "is_live": False
        },
        "market": {
            "type": market_type,
            "name": "Match Result",
            "selections": selections
        },
        "collected_at": datetime.utcnow().isoformat()
    }
