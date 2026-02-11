"""
Browser context sem proxy para execução local
Usa a conexão de internet normal da máquina
"""
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def get_browser_context_local(playwright):
    """
    Cria contexto do browser SEM proxy para uso local
    Usa apenas stealth básico
    """
    # Configuração simples do browser
    launch_args = {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
        "timeout": 120000  # 2 minutos
    }
    
    logger.info("🏠 Iniciando browser LOCAL (sem proxy)")
    browser = playwright.chromium.launch(**launch_args)
    
    # Contexto com user agent realista
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        ignore_https_errors=True,
    )
    
    # Script anti-detecção básico
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
    """)
    
    return browser, context
