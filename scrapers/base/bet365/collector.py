from playwright.sync_api import sync_playwright, TimeoutError
import logging

logger = logging.getLogger(__name__)

BET365_URL = "https://www.bet365.bet.br/"

def collect_futebol_1x2(max_items=5):
    collected = []

    with sync_playwright() as p:
        # Dica: Em Home Server, tente não usar headless=True na primeira vez para debugar visualmente
        # ou use o 'scrapers/shared/browser.py' que você já configurou
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        # Contexto com User-Agent comum para evitar bloqueio imediato
        context = browser.new_context(
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = context.new_page()

        try:
            logger.info("Acessando Bet365...")
            page.goto(BET365_URL, timeout=60000)
            
            # 1. Navegação: Precisamos garantir que estamos no Futebol
            # Clicar no ícone de futebol se necessário, ou navegar direto pra URL da liga
            # Exemplo de URL direta (muito melhor que navegar):
            # page.goto("https://www.bet365.com/#/AC/B1/C1/D100/E40/", ...) # Exemplo fictício de liga

            # Espera a grid de jogos carregar. 
            # Evite seletores como '.gl-MarketGroup', tente algo genérico que contenha texto
            page.wait_for_selector("div:has-text('Futebol')", timeout=15000)
            page.wait_for_timeout(5000) # Deixa o JS terminar de montar a tela

            # 2. Estratégia de Seleção Visual (A mais robusta)
            # Ao invés de classes loucas, pegamos os containers de jogos
            # Nota: Você precisará inspecionar o HTML atual para ajustar a classe 'pai' do jogo.
            # A Bet365 costuma usar uma estrutura de Grid.
            
            # Exemplo genérico de iteração (Pseudocódigo ajustável):
            # Localiza todas as linhas que parecem ter Odds
            # Geralmente são divs com display grid ou flex
            
            # Vamos tentar pegar todos os elementos que têm nomes de times e odds
            # Dica: Use o inspector do Chrome no seu PC e procure a classe que envolve a LINHA do jogo
            # Atualmente algo como '.rcl-ParticipantFixtureDetails' ou similar
            
            match_rows = page.locator("div.rcl-ParticipantFixtureDetails").all() # Exemplo de classe, verifique!
            
            logger.info(f"Encontrados {len(match_rows)} potenciais jogos")

            for row in match_rows[:max_items]:
                # Extração via Texto relativo
                text = row.inner_text().split('\n')
                # O texto geralmente vem: "12:00", "Time A", "Time B", "1.50", "3.00", "4.00"
                
                if len(text) > 3:
                    collected.append({
                        "raw_text": text, # Salva o texto bruto pra debug
                        "market": "1X2",
                        "source": "bet365_visual"
                    })

        except TimeoutError:
            logger.error("Timeout carregando Bet365")
        except Exception as e:
            logger.error(f"Erro no scraping visual: {e}")
        finally:
            browser.close()

    return collected