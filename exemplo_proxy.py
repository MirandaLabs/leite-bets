"""
Exemplo de Uso do Proxy Manager
Demonstra como usar proxies rotativos e estáticos nos scrapers
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.shared.proxy_manager import proxy_manager
from scrapers.shared.logger import logger


def exemplo_basico():
    """
    Exemplo básico de uso do proxy
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 1: Uso Básico")
    print("="*60)
    
    # Obter configuração de proxy para um scraper
    config = proxy_manager.get_proxy_config("betano")
    
    if config:
        print(f"\n✅ Configuração obtida:")
        print(f"   Server: {config['server']}")
        if 'username' in config:
            print(f"   Com autenticação: Sim")
        print()
    else:
        print("\n❌ Nenhuma configuração de proxy disponível")


def exemplo_multiplos_scrapers():
    """
    Exemplo com múltiplos scrapers
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 2: Múltiplos Scrapers")
    print("="*60)
    
    scrapers = ["betano", "superbet", "esportesdasorte", "bet365"]
    
    print("\n🔄 Obtendo configurações para cada scraper:\n")
    
    for scraper in scrapers:
        config = proxy_manager.get_proxy_config(scraper)
        if config:
            proxy = proxy_manager.get_used_proxy(scraper)
            print(f"   ✅ {scraper:15} → {proxy}")


def exemplo_sticky_sessions():
    """
    Demonstra sticky sessions (modo rotativo)
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 3: Sticky Sessions")
    print("="*60)
    
    if proxy_manager.mode != "rotating":
        print("\n⚠️  Este exemplo requer PROXY_MODE=rotating")
        return
    
    scraper = "demo_scraper"
    
    print(f"\n1️⃣ Primeira chamada:")
    config1 = proxy_manager.get_proxy_config(scraper)
    if config1 and 'username' in config1:
        print(f"   Username: {config1['username']}")
    
    print(f"\n2️⃣ Segunda chamada (mesma sessão):")
    config2 = proxy_manager.get_proxy_config(scraper)
    if config2 and 'username' in config2:
        print(f"   Username: {config2['username']}")
    
    if config1 and config2:
        if config1.get('username') == config2.get('username'):
            print(f"\n   ✅ Sticky session funcionando! Username mantido.")
        else:
            print(f"\n   ⚠️  Usernames diferentes (sticky pode estar desabilitado)")


def exemplo_reset_session():
    """
    Demonstra como resetar sessão para obter novo IP
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 4: Reset de Sessão")
    print("="*60)
    
    if proxy_manager.mode != "rotating":
        print("\n⚠️  Este exemplo requer PROXY_MODE=rotating")
        return
    
    scraper = "test_reset"
    
    print(f"\n1️⃣ Configuração inicial:")
    config1 = proxy_manager.get_proxy_config(scraper)
    if config1 and 'username' in config1:
        print(f"   Username: {config1['username']}")
    
    print(f"\n2️⃣ Resetando sessão...")
    proxy_manager.reset_session(scraper)
    
    print(f"\n3️⃣ Nova configuração (novo IP):")
    config2 = proxy_manager.get_proxy_config(scraper)
    if config2 and 'username' in config2:
        print(f"   Username: {config2['username']}")
    
    if config1 and config2:
        if config1.get('username') != config2.get('username'):
            print(f"\n   ✅ Sessão resetada! Novo IP será usado.")
        else:
            print(f"\n   ⚠️  Username não mudou")


def exemplo_informacoes():
    """
    Exibe informações sobre configuração atual
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 5: Informações da Configuração")
    print("="*60)
    
    info = proxy_manager.get_info()
    
    print(f"\n📊 Configuração atual:")
    print(f"   Modo: {info['mode'].upper()}")
    print(f"   Habilitado: {'Sim' if info['enabled'] else 'Não'}")
    
    if info['mode'] == 'rotating':
        print(f"   Server: {info['server']}:{info['port']}")
        print(f"   Sticky Sessions: {'Sim' if info['sticky_sessions'] else 'Não'}")
        print(f"   Sessões Ativas: {info['active_sessions']}")
    else:
        print(f"   Proxies Estáticos: {info['static_proxies_count']}")
        print(f"   Carregados: {'Sim' if info['proxies_loaded'] else 'Não'}")


def exemplo_playwright():
    """
    Exemplo de uso com Playwright
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 6: Uso com Playwright")
    print("="*60)
    
    print("""
    # Código de exemplo para usar com Playwright:
    
    from playwright.sync_api import sync_playwright
    from scrapers.shared.proxy_manager import proxy_manager
    
    # Obter configuração de proxy
    proxy_config = proxy_manager.get_proxy_config("meu_scraper")
    
    with sync_playwright() as p:
        # Passar configuração ao browser
        browser = p.chromium.launch(
            headless=True,
            proxy=proxy_config  # ← Aqui!
        )
        
        context = browser.new_context()
        page = context.new_page()
        
        # Seu código aqui...
        page.goto("https://example.com")
        
        browser.close()
    """)


def exemplo_condicional():
    """
    Exemplo de uso condicional (com/sem proxy)
    """
    print("\n" + "="*60)
    print("📖 EXEMPLO 7: Uso Condicional")
    print("="*60)
    
    print("""
    # Código que funciona com ou sem proxy:
    
    from scrapers.shared.proxy_manager import proxy_manager
    
    def meu_scraper():
        # Tenta obter proxy
        proxy_config = proxy_manager.get_proxy_config("meu_scraper")
        
        if proxy_config:
            print("✅ Usando proxy")
            # Iniciar browser com proxy
        else:
            print("⚠️  Sem proxy configurado")
            # Iniciar browser sem proxy
        
        # Resto do código...
    """)


def main():
    """
    Executa todos os exemplos
    """
    print("\n" + "="*60)
    print("🎓 EXEMPLOS DE USO DO PROXY MANAGER")
    print("="*60)
    
    try:
        exemplo_basico()
        exemplo_multiplos_scrapers()
        exemplo_sticky_sessions()
        exemplo_reset_session()
        exemplo_informacoes()
        exemplo_playwright()
        exemplo_condicional()
        
        print("\n" + "="*60)
        print("✅ TODOS OS EXEMPLOS EXECUTADOS!")
        print("="*60)
        
        print("\n💡 DICAS:")
        print("   - Use PROXY_MODE=rotating para milhares de IPs")
        print("   - Ative PROXY_STICKY_SESSION=true para manter IPs por sessão")
        print("   - Use reset_session() para forçar mudança de IP")
        print("   - Teste com: python test_proxy.py")
        print()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
