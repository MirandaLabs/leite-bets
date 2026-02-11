from playwright.sync_api import sync_playwright, TimeoutError
import logging

MAX_RETRIES = 3
logger = logging.getLogger(__name__)

SUPERBET_URL = "https://superbet.bet.br/apostas/futebol/brasil/brasileiro-serie-a/todos?cpi=4ivzYkpyZ0KYH5vHOJ6qVP&ct=m"

def collect():
    """Collect match odds from Superbet"""
    
    with sync_playwright() as p:
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔄 Tentativa {attempt}/{MAX_RETRIES}")
            
            try:
                browser, context = get_browser_context(p)
                page = context.new_page()
                
                # Configura timeout
                page.set_default_timeout(90000)  # 90 segundos
                page.set_default_navigation_timeout(90000)
                
                logger.info(f"Navegando para: {SUPERBET_URL}")
                
                # Tenta navegar com estratégia de fallback
                try:
                    response = page.goto(
                        SUPERBET_URL,
                        timeout=90000,
                        wait_until="domcontentloaded"
                    )
                    
                    if response and response.status != 200:
                        logger.error(f"❌ Status HTTP: {response.status}")
                        raise ValueError(f"Status {response.status}")
                        
                except Exception as nav_error:
                    logger.warning(f"⚠️ Erro na navegação: {nav_error}")
                    # Tenta recarregar
                    page.reload(timeout=90000, wait_until="domcontentloaded")
                
                # Aguarda um tempo para carregar
                page.wait_for_timeout(5000)
                
                # Verifica se carregou
                content = page.content()
                logger.info(f"📄 Conteúdo carregado: {len(content)} bytes")
                
                if len(content) < 5000:
                    raise ValueError("Conteúdo insuficiente")
                
                # Tenta encontrar elementos
                try:
                    page.wait_for_selector("div.event-card", timeout=30000)
                except:
                    # Tenta seletor alternativo
                    page.wait_for_selector("div[class*='event']", timeout=30000)
                
                # Processa dados
                matches = parse_matchresult_from_main_page(content)
                
                if matches:
                    logger.info(f"✅ Sucesso! {len(matches)} jogos coletados")
                    browser.close()
                    return matches
                else:
                    raise ValueError("Nenhum dado coletado")
                    
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {attempt}: {str(e)}")
                
                # Fecha browser se existir
                try:
                    browser.close()
                except:
                    pass
                
                if attempt == MAX_RETRIES:
                    raise ScraperError(f"Falha após {MAX_RETRIES} tentativas")
                
                logger.info(f"⏱️ Aguardando 3 segundos...")
                time.sleep(3)