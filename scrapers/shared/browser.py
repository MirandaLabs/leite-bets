# scrapers/shared/browser.py

from playwright.sync_api import sync_playwright
from scrapers.shared.proxy_manager import ProxyManager

# Instanciamos o gerenciador globalmente para ele carregar a lista de IPs apenas uma vez
proxy_manager = ProxyManager()

def get_browser_context(playwright, user_data_dir="storage/browser", scraper_name=None):
    """
    Cria contexto do browser com proxy aleatório estático (Webshare) e stealth mode
    """
    # 1. Pega uma URL de proxy aleatória do nosso novo gerenciador
    proxy_url = proxy_manager.get_random_proxy()
    
    # 2. Formata para o formato de dicionário que o Playwright exige
    proxy_config = None
    if proxy_url:
        proxy_config = {"server": proxy_url}
    
    # 3. Inicia o Browser
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process"
        ],
        proxy=proxy_config  # Injeta o proxy configurado
    )
    
    # 4. Configura o Contexto (Sessão)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="131", "Google Chrome";v="131"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }
    )
    
    # 5. OTIMIZAÇÃO DE BANDA OBRIGATÓRIA (Economiza 80% do tráfego do Proxy)
    # Aborta carregamento de mídias e estilos inúteis para o scraping
    context.route(
        "**/*.{png,jpg,jpeg,gif,webp,svg,ico,woff,woff2,ttf,css,mp4,webm}", 
        lambda route: route.abort()
    )
    # Aborta trackers para não gastar requisições do seu limite
    context.route("**/*google-analytics*", lambda route: route.abort())
    context.route("**/*facebook*", lambda route: route.abort())
    context.route("**/*googletagmanager*", lambda route: route.abort())
    
    # 6. Scripts de Stealth (Anti-Detecção)
    context.add_init_script("""
        // Overwrite the `navigator.webdriver` property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Overwrite the `plugins` property
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Overwrite the `languages` property
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
    """)

    return browser, context