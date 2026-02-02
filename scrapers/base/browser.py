from playwright.sync_api import sync_playwright
from scrapers.shared.proxy_manager import get_proxy_config


def get_browser_context(playwright, user_data_dir="storage/browser", scraper_name=None):
    """
    Cria contexto do browser com proxy aleatório
    
    Args:
        playwright: Instância do Playwright
        user_data_dir: Diretório para dados do browser
        scraper_name: Nome do scraper (para tracking de proxy)
    """
    # Obter configuração de proxy aleatório
    proxy_config = get_proxy_config(scraper_name)
    
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ],
        proxy=proxy_config  # Configurar proxy no browser
    )
    
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo"
    )

    return browser, context
