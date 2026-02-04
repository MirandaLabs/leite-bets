from playwright.sync_api import sync_playwright
import logging
from datetime import datetime
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
            
            # Tentar networkidle mas não bloquear se demorar
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
                logger.info("✅ Network idle alcançado")
            except Exception as e:
                logger.warning(f"⚠️  Network idle timeout (continuando): {e}")
            
            page.wait_for_timeout(3000)
            
            # Fechar modal se aparecer
            try:
                modal = page.query_selector("div.modal-overlay")
                if modal and modal.is_visible():
                    modal.click()
                    page.wait_for_timeout(1000)
            except:
                pass
            
            # Screenshot e HTML dump
            import os
            os.makedirs("storage/debug", exist_ok=True)
            page.screenshot(path="storage/debug/esportesdasorte_simple.png")
            logger.info("📸 Screenshot: storage/debug/esportesdasorte_simple.png")
            
            # Dump HTML
            html_content = page.content()
            with open("storage/debug/esportesdasorte_simple.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("📄 HTML dump: storage/debug/esportesdasorte_simple.html")
            
            # Buscar jogos - tentar múltiplos seletores
            logger.info("Procurando jogos...")
            
            selectors = [
                "div.fixture-body.flex-container",
                "div.fixture-body",
                "div.fixture-container",
                "div[class*='fixture']",
                "div[class*='match']",
                "div[class*='event']"
            ]
            
            fixtures = []
            for selector in selectors:
                fixtures = page.query_selector_all(selector)
                if len(fixtures) > 0:
                    logger.info(f"✅ Encontrados {len(fixtures)} elementos com seletor: {selector}")
                    break
                else:
                    logger.info(f"❌ Seletor '{selector}' não encontrou elementos")
            
            if len(fixtures) == 0:
                logger.error("❌ Nenhum jogo encontrado com nenhum seletor - possível bloqueio ou página vazia")
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
                    
                    # Formato esperado pela API
                    event_name = f"{home} vs {away}"
                    odds_data.append({
                        "source": "esportesdasorte",
                        "sport": "soccer",
                        "competition": "Brasileiro Série A",
                        "event": {
                            "id": event_name.lower().replace(" ", "-"),
                            "name": event_name,
                            "start_time": None,
                            "status": "upcoming"
                        },
                        "market": {
                            "type": "1X2",
                            "name": "Resultado Final",
                            "selections": [
                                {"key": "1", "name": home, "odd": float(home_odd.replace(",", "."))},
                                {"key": "X", "name": "Empate", "odd": float(draw_odd.replace(",", "."))},
                                {"key": "2", "name": away, "odd": float(away_odd.replace(",", "."))}
                            ]
                        },
                        "collected_at": datetime.utcnow().isoformat()
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
