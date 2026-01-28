# Superbet Scraper

Scraper for collecting double chance odds from Superbet (superbet.bet.br).

## Overview

This scraper collects double chance odds (1X, 12, X2) from Brazilian Serie A matches on Superbet.

## Structure

- `collector.py` - Main scraping logic using Playwright
- `parser.py` - HTML parsing and data extraction
- `selectors.py` - CSS selectors for Superbet elements
- `app.py` - Entry point for running the scraper

## How it works

1. Opens the Superbet Brazilian Serie A page
2. Finds all event cards on the main page
3. Clicks on each event to open the detailed view
4. Looks for the double chance market with 3 options:
   - "1 ou Empate" (Home or Draw) - mapped to 1X
   - "Empate ou 2" (Draw or Away) - mapped to X2
   - "1 ou 2" (Home or Away) - mapped to 12
5. Extracts team names and odds
6. Returns back to main page and continues with next event

## Running

```bash
python -m scrapers.base.superbet.app
```

## Configuration

- URL: `https://superbet.bet.br/apostas/futebol/brasil/brasileiro-serie-a/todos?cpi=4ivzYkpyZ0KYH5vHOJ6qVP&ct=m`
- Browser: Chromium (Playwright)
- Headless mode: Set to `False` by default for debugging, change to `True` in production

## Selectors

The scraper uses the following CSS selectors:

- Event card: `div.event-card.e2e-event-row`
- Team names: `div.e2e-event-team1-name`, `div.e2e-event-team2-name`
- Market container: `div.market.single-market-card__market-line`
- Odd name: `span.odd-button__odd-name.e2e-odd-name`
- Odd value: `span.odd-button__odd-value span`

## Output format

The scraper outputs data in the standard Odds format:

```python
{
    "source": "superbet",
    "sport": "football",
    "competition": "brasileirao-serie-a",
    "event": {
        "id": "superbet_team1_vs_team2",
        "name": "Team1 vs Team2",
        "start_time": null,
        "is_live": false
    },
    "market": {
        "type": "Double Chance",
        "name": "Double Chance",
        "selections": [
            {"key": "1X", "name": "Home or Draw", "odd": 1.60},
            {"key": "X2", "name": "Draw or Away", "odd": 1.36},
            {"key": "12", "name": "Home or Away", "odd": 1.39}
        ]
    },
    "collected_at": "2026-01-28T12:00:00"
}
```

## Notes

- The scraper is rate-limited to process the first 10 events by default (configurable in collector.py)
- Each event requires a page navigation, so execution time is proportional to the number of events
- Error handling is in place to skip problematic events and continue processing
- The browser closes automatically after completion or on error
