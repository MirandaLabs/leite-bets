# Esportes da Sorte Scraper

Scraper for collecting double chance odds from Esportes da Sorte (esportesdasorte.bet.br).

## Overview

This scraper collects double chance odds (1X, 12, X2) from Brazilian Serie A matches on Esportes da Sorte.

## Structure

- `collector.py` - Main scraping logic using Playwright
- `parser.py` - HTML parsing and data extraction
- `selectors.py` - CSS selectors for Esportes da Sorte elements
- `app.py` - Entry point for running the scraper

## How it works

1. Opens the Esportes da Sorte Brazilian Serie A page
2. Finds all match cards on the main page
3. Clicks on each match to open the detailed view
4. Looks for the double chance market with 3 options:
   - "Casa Ou Empate" (Home or Draw) - mapped to 1X
   - "Casa Ou Fora" (Home or Away) - mapped to 12
   - "Empate Ou Fora" (Draw or Away) - mapped to X2
5. Extracts team names and odds
6. Returns back to main page and continues with next match

## Running

```bash
python -m scrapers.base.esportesdasorte.app
```

## Configuration

- URL: `https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026`
- Browser: Chromium (Playwright)
- Headless mode: Set to `True` for production (Docker)

## Selectors

The scraper uses the following CSS selectors:

- Match container: `div.element.flex-item.match`
- Team names: `a.team-name div.text.truncate`
- Bet type group: `div.flex-container.bet-type-btn-group`
- Bet button: `a.bet-btn`
- Bet text: `span.bet-btn-text`
- Bet odd: `span.bet-btn-odd`

## Output format

The scraper outputs data in the standard Odds format:

```python
{
    "source": "esportesdasorte",
    "sport": "football",
    "competition": "brasileirao-serie-a",
    "event": {
        "id": "esportesdasorte_team1_vs_team2",
        "name": "Team1 vs Team2",
        "start_time": null,
        "is_live": false
    },
    "market": {
        "type": "Double Chance",
        "name": "Double Chance",
        "selections": [
            {"key": "1X", "name": "Home or Draw", "odd": 1.57},
            {"key": "12", "name": "Home or Away", "odd": 1.37},
            {"key": "X2", "name": "Draw or Away", "odd": 1.37}
        ]
    },
    "collected_at": "2026-01-28T12:00:00"
}
```

## Notes

- The scraper is rate-limited to process the first 10 matches by default (configurable in collector.py)
- Each match requires a page navigation, so execution time is proportional to the number of matches
- Error handling is in place to skip problematic matches and continue processing
- The browser closes automatically after completion or on error
