from playwright.sync_api import sync_playwright
import logging
from scrapers.shared.errors import ScraperError
from scrapers.shared.browser import get_browser_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ESPORTESDASORTE_URL = "https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026"


def collect():
    """Collect basic 1X2 odds from Esportes da Sorte - versão simplificada."""
    
    with sync_playwright() as p:
        browser, context = get_browser_context(p, scraper_name="esportesdasorte")
        page = context.new_page()

        try:
            logger.info(f"Abrindo: {ESPORTESDASORTE_URL}")
            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            
            # Fechar modal se aparecer
            try:
                modal = page.query_selector("div.modal-overlay")
                if modal and modal.is_visible():
                    modal.click()
                    page.wait_for_timeout(1000)
            except:
                pass
            
            # Screenshot
            import os
            os.makedirs("storage/debug", exist_ok=True)
            page.screenshot(path="storage/debug/esportesdasorte_simple.png")
            logger.info("📸 Screenshot: storage/debug/esportesdasorte_simple.png")
            
            # Buscar jogos (fixture-body)
            logger.info("Procurando jogos...")
            fixtures = page.query_selector_all("div.fixture-body")
            logger.info(f"✅ Encontrados {len(fixtures)} jogos")
            
            if len(fixtures) == 0:
                logger.error("❌ Nenhum jogo encontrado - possível bloqueio")
                page.screenshot(path="storage/debug/esportesdasorte_no_games.png")
                return []
            
            odds_data = []
            
            # Processar cada jogo (máximo 3 para teste)
            for i, fixture in enumerate(fixtures[:3]):
                try:
                    # Pegar times
                    teams = fixture.query_selector_all("a.team-name div.text.truncate")
                    if len(teams) < 2:
                        continue
                    
                    home = teams[0].inner_text().strip()
                    away = teams[1].inner_text().strip()
                    
                    # Pegar odds 1X2 (bt-col-3 = Resultado)
                    result_col = fixture.query_selector("div.bet-type.bt-col-3")
                    if not result_col:
                        logger.warning(f"Sem odds para {home} vs {away}")
                        continue
                    
                    odds_buttons = result_col.query_selector_all("a.bet-btn")
                    if len(odds_buttons) < 3:
                        logger.warning(f"Odds incompletas para {home} vs {away}")
                        continue
                    
                    home_odd = odds_buttons[0].query_selector("span.bet-btn-odd").inner_text().strip()
                    draw_odd = odds_buttons[1].query_selector("span.bet-btn-odd").inner_text().strip()
                    away_odd = odds_buttons[2].query_selector("span.bet-btn-odd").inner_text().strip()
                    
                    odds_data.append({
                        "home": home,
                        "away": away,
                        "market": "1X2",
                        "bookmaker": "Esportes da Sorte",
                        "home_odd": float(home_odd),
                        "draw_odd": float(draw_odd),
                        "away_odd": float(away_odd)
                    })
                    
                    logger.info(f"✅ {home} vs {away}: {home_odd} / {draw_odd} / {away_odd}")
                    
                except Exception as e:
                    logger.error(f"Erro no jogo {i+1}: {str(e)}")
                    continue
            
            logger.info(f"🎯 Total coletado: {len(odds_data)} jogos")
            return odds_data
            
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            page.screenshot(path="storage/debug/esportesdasorte_error.png")
            raise ScraperError(f"Erro coletando Esportes da Sorte: {str(e)}")
        finally:
            browser.close()
