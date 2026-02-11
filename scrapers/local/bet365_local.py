"""
Bet365 collector para execução local sem proxy
"""
from playwright.sync_api import sync_playwright
import logging
from scrapers.local.browser_no_proxy import get_browser_context_local

logger = logging.getLogger(__name__)

BET365_URL = "https://www.bet365.bet.br/#/AC/B1/C1/D100/E40/"


def collect_bet365_local():
    """Coleta odds da Bet365 usando conexão local (sem proxy)"""
    logger.info("🇧🇷 Iniciando coleta BET365 (conexão local)")
    
    with sync_playwright() as p:
        browser, context = get_browser_context_local(p)
        page = context.new_page()

        try:
            logger.info(f"Navegando para: {BET365_URL}")
            page.goto(BET365_URL, timeout=60000)
            
            # Aguarda lista de jogos
            page.wait_for_selector("div.rcl-ParticipantFixtureDetails", timeout=15000)
            logger.info("✅ Lista de jogos carregada")
            
            # TODO: Implementar extração completa
            # Por enquanto retorna vazio
            logger.warning("⚠️ Parser da Bet365 ainda não implementado completamente")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta Bet365: {str(e)}")
            return []
        finally:
            browser.close()
