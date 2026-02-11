# scrapers/shared/browser.py

from playwright.sync_api import sync_playwright
from scrapers.shared.proxy_manager import ProxyManager
import logging

logger = logging.getLogger(__name__)

# Instanciamos o gerenciador globalmente
proxy_manager = ProxyManager()

def get_browser_context(playwright, user_data_dir="storage/browser", scraper_name=None):
    """
    Cria contexto do browser com proxy aleatório funcional
    """
    # 1. Pega uma URL de proxy funcional
    proxy_url = proxy_manager.get_random_proxy()
    
    # 2. Configuração do browser
    launch_args = {
        "headless": True,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--metrics-recording-only",
            "--no-first-run",
            "--mute-audio",
            "--hide-scrollbars",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--disable-javascript"  # Desabilita JS para sites que usam Cloudflare
        ],
        "timeout": 120000  # 2 minutos
    }
    
    # 3. Adiciona proxy se disponível
    if proxy_url:
        # Parse a URL do proxy para extrair host e porta
        from urllib.parse import urlparse
        parsed = urlparse(proxy_url)
        
        launch_args["proxy"] = {
            "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            "username": parsed.username,
            "password": parsed.password
        }
        logger.info(f"🔧 Proxy configurado para: {parsed.hostname}:{parsed.port}")
    
    # 4. Inicia o Browser com timeout maior
    browser = playwright.chromium.launch(**launch_args)
    
    # 5. Configura o Contexto (Sessão)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        ignore_https_errors=True,  # Ignora erros de certificado
        java_script_enabled=False,  # Desabilita JS inicialmente
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    )
    
    # 6. ROTAS OBRIGATÓRIAS para economizar banda e evitar detecção
    # Primeiro habilita o JS para sites que precisam
    def enable_js_on_main_page(route):
        if route.request.url.startswith("https://superbet.bet.br"):
            # Para a Superbet, permita o JS
            route.continue_()
        else:
            # Para outros recursos, bloqueie
            route.abort()
    
    context.route("**/*", enable_js_on_main_page)
    
    # 7. Scripts de Stealth (Anti-Detecção)
    context.add_init_script("""
        // Remove webdriver property
        delete Object.getPrototypeOf(navigator).webdriver;
        
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Spoof languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    return browser, context