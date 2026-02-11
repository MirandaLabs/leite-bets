"""
Superbet collector para execução local sem proxy
"""
from playwright.sync_api import sync_playwright, TimeoutError
import logging
from scrapers.local.browser_no_proxy import get_browser_context_local
from scrapers.base.superbet.parser import parse_matchresult_from_main_page

logger = logging.getLogger(__name__)

SUPERBET_URL = "https://superbet.bet.br/apostas/futebol/brasil/brasileiro-serie-a/todos?cpi=4ivzYkpyZ0KYH5vHOJ6qVP&ct=m"


def collect_superbet_local():
    """Coleta odds da Superbet usando conexão local (sem proxy)"""
    logger.info("🇧🇷 Iniciando coleta SUPERBET (conexão local)")
    
    with sync_playwright() as p:
        browser, context = get_browser_context_local(p)
        page = context.new_page()

        try:
            logger.info(f"Navegando para: {SUPERBET_URL}")
            
            response = page.goto(
                SUPERBET_URL,
                timeout=90000,
                wait_until="domcontentloaded"
            )
            
            if response and response.status == 200:
                logger.info("✅ Página Superbet carregada")
                
                # Aguarda conteúdo carregar com mais tempo
                page.wait_for_timeout(5000)
                
                # Tenta aguardar por elementos específicos (event cards)
                try:
                    page.wait_for_selector("div.event-card", timeout=10000)
                    logger.info("✅ Event cards detectados")
                except:
                    logger.warning("⚠️ Event cards não detectados, continuando mesmo assim...")
                
                html = page.content()
                logger.info(f"HTML capturado: {len(html)} bytes")
                
                # Parse usando o parser existente
                matches = parse_matchresult_from_main_page(html)
                
                if matches:
                    logger.info(f"✅ Encontrados {len(matches)} jogos na Superbet")
                else:
                    logger.warning("⚠️ Nenhum jogo encontrado no parser da Superbet")
                
                return matches
            else:
                logger.error(f"❌ Status HTTP inválido: {response.status if response else 'None'}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na coleta Superbet: {str(e)}")
            return []
        finally:
            browser.close()
