from playwright.sync_api import sync_playwright, TimeoutError
import logging
import time
from scrapers.base.superbet.parser import parse_matchresult_from_main_page
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

from playwright_stealth import stealth_sync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPERBET_URL = "https://superbet.bet.br/apostas/futebol/brasil/brasileiro-serie-a/todos?cpi=4ivzYkpyZ0KYH5vHOJ6qVP&ct=m"
MAX_RETRIES = 3  # Número máximo de vezes que ele vai tentar com IPs diferentes

def collect():
    """Collect match odds from Superbet using Playwright with proxy rotation and auto-retry."""
    
    with sync_playwright() as p:
        # Loop de tentativas
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔄 Tentativa {attempt}/{MAX_RETRIES} para Superbet...")
            
            # O get_browser_context vai sortear um NOVO IP a cada tentativa
            browser, context = get_browser_context(p, scraper_name="superbet")
            
            try:
                page = context.new_page()
                stealth_sync(page)
                logger.info(f"Opening Superbet URL: {SUPERBET_URL}")
                page.goto(SUPERBET_URL, timeout=60000, wait_until="domcontentloaded")
                
                # 1. CHECAGEM DE BLOQUEIO (WAF/Cloudflare)
                html = page.content()
                if len(html) < 5000:
                    logger.warning(f"⚠️ HTML muito pequeno ({len(html)} bytes). Proxy bloqueado!")
                    # Lançamos um erro proposital para cair no 'except', fechar o browser e tentar outro IP
                    raise ValueError("Bloqueio detectado (HTML curto).")

                # 2. Tentar fechar o popup de cookies (se existir)
                try:
                    logger.info("Checking for cookie consent popup...")
                    accept_button = page.wait_for_selector(
                        "button#onetrust-accept-btn-handler",
                        timeout=5000,
                        state="visible"
                    )
                    if accept_button:
                        logger.info("Closing cookie consent popup...")
                        accept_button.click()
                        page.wait_for_timeout(2000)
                except Exception:
                    logger.info("No cookie popup found or already closed.")
                
                # 3. Esperar os cards dos jogos carregarem na tela
                logger.info("Waiting for event cards to load...")
                page.wait_for_selector("div.event-card.e2e-event-row", timeout=30000)
                logger.info("✅ Elementos carregados com sucesso!")
                
                page.wait_for_timeout(3000)
                
                # 4. Extrair o HTML limpo e passar pro Parser
                final_html = page.content()
                logger.info(f"HTML retrieved ({len(final_html)} bytes), parsing matches...")
                matches = parse_matchresult_from_main_page(final_html)
                
                logger.info(f"🎯 Total matches collected: {len(matches)}")
                
                # SE CHEGOU AQUI, DEU CERTO! Retornamos os dados e o loop encerra.
                return matches

            except Exception as e:
                logger.error(f"❌ Erro na tentativa {attempt}: {str(e)}")
                
                # Salva um print só para debug da falha específica
                import os
                os.makedirs("storage/debug", exist_ok=True)
                try:
                    page.screenshot(path=f"storage/debug/superbet_fail_try_{attempt}.png")
                except:
                    pass
                
                # Se for a última tentativa, estouramos o erro pro sistema saber que falhou de vez
                if attempt == MAX_RETRIES:
                    logger.error("🚨 Todas as tentativas falharam. Abortando Superbet.")
                    raise ScraperError(f"Falha na Superbet após {MAX_RETRIES} tentativas: {str(e)}")
                
                logger.info("Trocando de IP e tentando novamente em 2 segundos...")
                time.sleep(2)
                
            finally:
                # OBRIGATÓRIO: Sempre fechar o browser no final de uma tentativa 
                # para não estourar a memória RAM do Railway e poder abrir um novo IP na próxima iteração
                if browser:
                    browser.close()