# scrapers/shared/browser.py

from playwright.sync_api import sync_playwright
from scrapers.shared.proxy_manager import ProxyManager
import logging

logger = logging.getLogger(__name__)

# Instanciamos o gerenciador
proxy_manager = ProxyManager()

def get_browser_context(playwright, scraper_name=None):
    """
    Cria contexto do browser com configuração otimizada
    """
    # Configuração base
    launch_args = {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-accelerated-2d-canvas",
            "--disable-setuid-sandbox",
            "--no-zygote",
            "--single-process",
        ],
        "timeout": 180000  # 3 minutos
    }
    
    # Obtém configuração do proxy
    proxy_config = proxy_manager.get_proxy_config()
    
    if proxy_config:
        logger.info(f"🎯 Usando proxy: {proxy_config['server']}")
        launch_args["proxy"] = proxy_config
    else:
        logger.warning("⚠️ Rodando sem proxy")
    
    # Inicia o browser
    browser = playwright.chromium.launch(**launch_args)
    
    # Configura o contexto
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
        java_script_enabled=True,
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    )
    
    # Configura rotas para bloquear recursos desnecessários
    def route_handler(route):
        url = route.request.url
        
        # Bloqueia recursos pesados
        if any(ext in url for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".mp4", ".webm"]):
            route.abort()
        # Permite tudo mais
        else:
            route.continue_()
    
    context.route("**/*", route_handler)
    
    # Scripts de stealth
    context.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
        
        // Mock Chrome runtime
        window.chrome = {
            runtime: {}
        };
    """)
    
    return browser, context