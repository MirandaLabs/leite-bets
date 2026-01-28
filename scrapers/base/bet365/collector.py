# scrapers/base/bet365/collector.py

from playwright.sync_api import sync_playwright
import logging
from . import selectors
from .parser import parse_odd_value, normalize_selection_name

logger = logging.getLogger(__name__)

def collect_double_chance(game_url: str):
    """
    Entra num jogo específico e extrai odds de Dupla Hipótese.
    """
    collected_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        # Use um contexto com User-Agent real
        context = browser.new_context(
             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
             viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        try:
            logger.info(f"Navegando para {game_url}")
            page.goto(game_url, timeout=60000, wait_until="domcontentloaded")
            
            # Tenta localizar o Header "Dupla Hipótese"
            # O seletor has_text é dinâmico do Playwright, não fica no arquivo selectors.py
            header = page.locator(selectors.MARKET_GROUP_BUTTON, has_text="Dupla Hipótese").first
            
            if not header.is_visible():
                logger.warning("Mercado Dupla Hipótese não encontrado visivelmente.")
                return []

            container = page.locator(selectors.MARKET_CONTAINER, has=header).first
            

            items = container.locator(selectors.PARTICIPANT_GENERAL).all()
            
            for item in items:
                raw_name = item.locator(selectors.PARTICIPANT_NAME).inner_text()
                raw_odd = item.locator(selectors.PARTICIPANT_ODDS).inner_text()
                
                odd_val = parse_odd_value(raw_odd)
                
                if odd_val:
                    collected_data.append({
                        "selection_raw": raw_name,
                        # "selection_key": normalize_selection_name(raw_name, home_team, away_team), 
                        "odd": odd_val,
                        "market": "Double Chance"
                    })

        except Exception as e:
            logger.error(f"Erro na coleta: {e}")
        finally:
            browser.close()
            
    return collected_data