"""
Betano collector para execução local sem proxy
"""
from playwright.sync_api import sync_playwright, TimeoutError
import logging
import time
from scrapers.local.browser_no_proxy import get_browser_context_local
from scrapers.base.betano.parser import parse_matchresult

logger = logging.getLogger(__name__)

BETANO_URL = "https://www.betano.bet.br/sport/futebol/brasil/brasileirao-serie-a-betano/10016/?bt=doublechance"


def collect_betano_local():
    """Coleta odds da Betano usando conexão local (sem proxy)"""
    logger.info("🇧🇷 Iniciando coleta BETANO (conexão local)")
    
    with sync_playwright() as p:
        browser, context = get_browser_context_local(p)
        page = context.new_page()

        try:
            logger.info(f"Navegando para: {BETANO_URL}")
            response = page.goto(BETANO_URL, timeout=60000, wait_until="networkidle")
            
            if response.status != 200:
                logger.error(f"❌ Status HTTP: {response.status}")
                return []
            
            logger.info("✅ Página carregada com sucesso")
            
            # Aguarda conteúdo
            try:
                page.wait_for_selector("div.tw-flex.tw-w-full.tw-flex-row.tw-items-start", timeout=15000)
                logger.info("✅ Container de eventos encontrado")
            except TimeoutError:
                logger.warning("⚠️ Container não encontrado, tentando seletor alternativo")
                page.wait_for_selector("div[class*='event']", timeout=10000)
            
            # Aguarda estabilização
            time.sleep(2)
            
            # Extrai HTML
            html = page.content()
            logger.info(f"HTML capturado: {len(html)} bytes")
            
            # Parse dos jogos
            matches = parse_matchresult(html)
            logger.info(f"✅ Encontrados {len(matches)} jogos na Betano")
            
            return matches
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta Betano: {str(e)}")
            return []
        finally:
            browser.close()
