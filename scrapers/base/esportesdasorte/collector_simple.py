from playwright.sync_api import sync_playwright
import logging
from datetime import datetime
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

logger = logging.getLogger(__name__)

# URL da lista de jogos
ESPORTESDASORTE_URL = "https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026"

def collect():
    """Coleta Odds de Dupla Hipótese da Esportes da Sorte"""
    odds_data = []
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="esportesdasorte")
        page = context.new_page()

        try:
            logger.info(f"Abrindo: {ESPORTESDASORTE_URL}")
            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
            
            # O SEGREDO: Esperar a tabela do Angular renderizar
            logger.info("Aguardando a tabela de jogos carregar...")
            page.wait_for_selector("div.fixture-body", timeout=20000)
            
            # Conta quantos jogos carregaram na tela
            match_rows = page.locator("div.fixture-body")
            match_count = match_rows.count()
            logger.info(f"✅ Encontrados {match_count} jogos. Iniciando extração...")
            
            # Vamos iterar sobre os primeiros jogos (limite para não demorar muito)
            for i in range(min(match_count, 5)):
                try:
                    # Precisamos re-localizar a linha toda vez que voltamos de uma página
                    page.wait_for_selector("div.fixture-body", timeout=15000)
                    row = page.locator("div.fixture-body").nth(i)
                    
                    # 1. Pegar os nomes dos times na lista
                    teams = row.locator("a.team-name div.text.truncate").all_inner_texts()
                    if len(teams) < 2:
                        continue
                    
                    home = teams[0].strip()
                    away = teams[1].strip()
                    logger.info(f"⚽ Processando: {home} vs {away}")
                    
                    # 2. Clicar no botão "Outros Mercados" (+1165, etc) para ir pro jogo
                    btn_outros = row.locator("a.other-btn")
                    if btn_outros.is_visible():
                        btn_outros.click()
                    else:
                        # Se não tiver botão "Outros", clica no nome do time
                        row.locator("a.team-name").first.click()
                    
                    # 3. Esperar a página interna do jogo carregar o mercado de Dupla Hipótese
                    # Procuramos a div que contém o texto específico
                    dc_container = page.locator("div.bet-type-btn-group", has_text="Casa Ou Empate").first
                    dc_container.wait_for(state="visible", timeout=15000)
                    
                    # 4. Extrair as odds baseadas no atributo "title" (muito mais seguro)
                    odd_1x = dc_container.locator("a[title='Casa Ou Empate'] span.bet-btn-odd").inner_text()
                    odd_12 = dc_container.locator("a[title='Casa Ou Fora'] span.bet-btn-odd").inner_text()
                    odd_x2 = dc_container.locator("a[title='Empate Ou Fora'] span.bet-btn-odd").inner_text()
                    
                    event_name = f"{home} vs {away}"
                    
                    odds_data.append({
                        "source": "esportesdasorte",
                        "sport": "soccer",
                        "competition": "Brasileiro Série A",
                        "event": {
                            "id": event_name.lower().replace(" ", "-"),
                            "name": event_name,
                            "status": "upcoming"
                        },
                        "market": {
                            "type": "Double Chance",
                            "name": "Dupla Hipótese",
                            "selections": [
                                {"key": "1X", "name": "Casa ou Empate", "odd": float(odd_1x.replace(",", "."))},
                                {"key": "12", "name": "Casa ou Fora", "odd": float(odd_12.replace(",", "."))},
                                {"key": "X2", "name": "Empate ou Fora", "odd": float(odd_x2.replace(",", "."))}
                            ]
                        },
                        "collected_at": datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"✔️ Odds coletadas: 1X({odd_1x}) | 12({odd_12}) | X2({odd_x2})")
                    
                    # 5. Voltar para a página da liga para pegar o próximo jogo
                    page.go_back(wait_until="domcontentloaded")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar jogo {i+1}: {str(e)}")
                    # Se der erro (ex: página não carregou), força recarregar a liga principal para não travar o loop
                    page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
            
            logger.info(f"🎯 Total coletado na Esportes da Sorte: {len(odds_data)} jogos")
            return odds_data
            
        except Exception as e:
            logger.error(f"Erro Fatal: {str(e)}")
            raise ScraperError(f"Erro coletando Esportes da Sorte: {str(e)}")
        finally:
            browser.close()
            # forçar re build