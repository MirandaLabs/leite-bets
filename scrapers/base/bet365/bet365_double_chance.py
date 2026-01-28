from playwright.sync_api import sync_playwright
import time

def run():
    LEAGUE_URL = "https://www.bet365.com/#/AC/B1/C1/D100/E40/" 
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"1. Acessando página da liga: {LEAGUE_URL}")
        page.goto(LEAGUE_URL, timeout=60000)
        
        # Espera carregar a lista de jogos
        page.wait_for_selector("div.rcl-ParticipantFixtureDetails", timeout=15000)
        
        # --- ETAPA 1: COLETAR LINKS DOS JOGOS ---
        match_links = []
        
        # Pega todos os containers de jogos na tela
        # A classe 'rcl-ParticipantFixtureDetails' costuma ser a área clicável do jogo
        game_elements = page.locator("div.rcl-ParticipantFixtureDetails").all()
        
        print(f"Jogos encontrados na lista: {len(game_elements)}")
        
        
        if len(game_elements) > 0:
            print("Entrando no primeiro jogo para extrair Dupla Hipótese...")
            game_elements[0].click()
            
            scrape_double_chance(page)
            
        browser.close()

def scrape_double_chance(page):
    """
    Função focada em achar e extrair a Dupla Hipótese na página interna do jogo.
    """
    try:
        print("Procurando mercado 'Dupla Hipótese'...")
        
        header = page.locator("div.gl-MarketGroupButton_Text", has_text="Dupla Hipótese").first
        
        if not header.is_visible():
            print("Mercado não visível imediatamente. Tentando aba 'Populares'...")
            return
        # 2. Localiza o CONTAINER pai desse header
        market_container = page.locator("div.gl-MarketGroup", has=page.locator("div", has_text="Dupla Hipótese")).first
        
        # 3. Extrai as Odds
        
        print("\n--- ODDS DUPLA HIPÓTESE ---")
        
        items = market_container.locator("div.gl-Participant_General").all()
        
        for item in items:
            # Tenta pegar o nome e a Odd
            name = item.locator(".gl-Participant_Name").inner_text()
            odd = item.locator(".gl-Participant_Odds").inner_text()
            
            print(f"{name} -> {odd}")
            
    except Exception as e:
        print(f"Erro ao extrair: {e}")

if __name__ == "__main__":
    run()