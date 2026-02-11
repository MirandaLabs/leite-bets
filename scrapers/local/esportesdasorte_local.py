"""
Esportes da Sorte collector para execução local sem proxy
"""
from playwright.sync_api import sync_playwright
import logging
from datetime import datetime
from scrapers.local.browser_no_proxy import get_browser_context_local

logger = logging.getLogger(__name__)

ESPORTESDASORTE_URL = "https://esportesdasorte.bet.br/ptb/bet/fixture-detail/soccer/brazil/brasileiro-serie-a-2026"


def collect_esportesdasorte_local():
    """Coleta odds da Esportes da Sorte usando conexão local (sem proxy)"""
    logger.info("🇧🇷 Iniciando coleta ESPORTES DA SORTE (conexão local)")
    
    odds_data = []
    
    with sync_playwright() as p:
        browser, context = get_browser_context_local(p)
        page = context.new_page()

        try:
            logger.info(f"Navegando para: {ESPORTESDASORTE_URL}")
            page.goto(ESPORTESDASORTE_URL, timeout=90000, wait_until="domcontentloaded")
            
            # Aguarda tabela Angular renderizar
            logger.info("Aguardando tabela de jogos...")
            page.wait_for_selector("div.fixture-body", timeout=30000)
            
            # Aguarda mais um pouco para garantir que tudo carregou
            page.wait_for_timeout(2000)
            
            # Conta jogos
            match_rows = page.locator("div.fixture-body")
            match_count = match_rows.count()
            logger.info(f"✅ Encontrados {match_count} jogos")
            
            # Limita a 5 jogos para ser mais rápido e evitar bloqueios
            for i in range(min(match_count, 5)):
                try:
                    # Re-localiza a lista de jogos após cada navegação
                    page.wait_for_selector("div.fixture-body", timeout=15000)
                    row = page.locator("div.fixture-body").nth(i)
                    
                    # Pega nomes dos times
                    teams = row.locator("a.team-name div.text.truncate").all_inner_texts()
                    if len(teams) < 2:
                        logger.warning(f"Jogo {i+1}: Times não encontrados")
                        continue
                    
                    home = teams[0].strip()
                    away = teams[1].strip()
                    logger.info(f"⚽ Processando: {home} vs {away}")
                    
                    # Clica no botão "other" que abre o modal com mais mercados
                    # Baseado no HTML: <a class="btn other-btn waves-effect waves-light modal-trigger">+1162</a>
                    # Estratégia: busca TODOS os botões other-btn e clica no índice correspondente
                    try:
                        page.wait_for_timeout(1500)  # Aguarda estabilização
                        
                        # Busca TODOS os botões other-btn na página (mais específico)
                        all_other_buttons = page.locator("a.btn.other-btn")
                        button_count = all_other_buttons.count()
                        
                        logger.info(f"DEBUG: Encontrados {button_count} botões 'other-btn' na página para jogo índice {i}")
                        
                        if button_count == 0:
                            logger.warning(f"⚠️ Nenhum botão 'other-btn' encontrado na página!")
                            # Tenta seletor alternativo
                            all_other_buttons = page.locator("div.element.other a")
                            button_count = all_other_buttons.count()
                            logger.info(f"DEBUG: Tentativa alternativa - encontrados {button_count} botões")
                        
                        # Verifica se o índice é válido
                        if i >= button_count:
                            logger.warning(f"⚠️ Índice {i} fora do range (total: {button_count})")
                            continue
                        
                        # Pega o botão específico pelo índice
                        other_button = all_other_buttons.nth(i)
                        
                        # Verifica se é visível com timeout maior
                        try:
                            is_visible = other_button.is_visible(timeout=3000)
                            logger.info(f"DEBUG: Botão {i} visível: {is_visible}")
                            
                            if not is_visible:
                                logger.warning(f"⚠️ Botão {i} não é visível, pulando...")
                                continue
                        except:
                            logger.warning(f"⚠️ Timeout ao verificar visibilidade do botão {i}")
                            continue
                        
                        # Scroll até o elemento
                        try:
                            other_button.scroll_into_view_if_needed(timeout=5000)
                            page.wait_for_timeout(800)
                            logger.info(f"DEBUG: Scroll realizado para botão {i}")
                        except Exception as scroll_err:
                            logger.warning(f"⚠️ Erro no scroll: {str(scroll_err)[:50]}")
                        
                        # Tenta clicar com force=True primeiro
                        try:
                            other_button.click(force=True, timeout=8000)
                            logger.info(f"✅ Clicou no botão 'Outro' (índice {i})")
                        except:
                            # Fallback: click com JavaScript
                            logger.info(f"DEBUG: Tentando click via JavaScript...")
                            page.evaluate("(el) => el.click()", other_button)
                            logger.info(f"✅ Clicou via JavaScript no botão {i}")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao clicar no botão 'Outro': {str(e)[:150]}")
                        continue
                    
                    # Aguarda a página de detalhes/modal carregar
                    # O botão abre um MODAL (não navega), então aguarda elementos do modal
                    logger.info(f"DEBUG: Aguardando modal abrir...")
                    page.wait_for_timeout(2000)
                    
                    # Tenta detectar se o modal abriu (pode ser modal-overlay, modal-content, etc)
                    try:
                        # Aguarda qualquer indicador de modal/overlay
                        modal_selectors = [
                            "div.modal.open",
                            "div[class*='modal'][class*='open']",
                            "div.modal-content",
                            "div[id*='modal']"
                        ]
                        
                        modal_opened = False
                        for modal_sel in modal_selectors:
                            if page.locator(modal_sel).count() > 0:
                                logger.info(f"DEBUG: Modal detectado com seletor: {modal_sel}")
                                modal_opened = True
                                break
                        
                        if not modal_opened:
                            logger.warning("DEBUG: Nenhum modal detectado, continuando mesmo assim...")
                            
                    except Exception as e:
                        logger.warning(f"DEBUG: Erro ao detectar modal: {e}")
                    
                    page.wait_for_timeout(1500)  # Aguarda um pouco mais para modal estabilizar
                    
                    # Debug: Verifica se realmente mudou algo após o click
                    current_url = page.url
                    logger.info(f"DEBUG: URL após click: {current_url}")
                    
                    # Salva HTML para debug (path do container)
                    try:
                        html_after_click = page.content()
                        debug_file = f"/app/storage/debug/esportes_after_click_{i}.html"
                        with open(debug_file, "w", encoding="utf-8") as f:
                            f.write(html_after_click)
                        logger.info(f"DEBUG: HTML salvo em {debug_file}")
                        
                        # Conta quantos textos "Dupla" aparecem no HTML
                        dupla_count = html_after_click.lower().count("dupla")
                        logger.info(f"DEBUG: Palavra 'dupla' aparece {dupla_count} vezes no HTML")
                    except Exception as e:
                        logger.warning(f"Erro ao salvar HTML debug: {e}")
                    
                    # Procura pelo botão/aba "Dupla chance" e clica nele
                    # Baseado no HTML: <button class="btn bet-btn waves-effect waves-light season-tabs-btn flex-item"> Dupla chance </button>
                    try:
                        # Procura pelo botão "Dupla chance"
                        dc_button_selectors = [
                            "button.season-tabs-btn:has-text('Dupla chance')",
                            "button.season-tabs-btn:has-text('dupla chance')",
                            "button:has-text('Dupla chance')",
                            "button:has-text('dupla chance')"
                        ]
                        
                        dc_button = None
                        for selector in dc_button_selectors:
                            try:
                                if page.locator(selector).count() > 0:
                                    dc_button = page.locator(selector).first
                                    logger.info(f"✅ Botão Dupla Chance encontrado com: {selector}")
                                    break
                            except:
                                continue
                        
                        if not dc_button:
                            logger.warning(f"⚠️ Botão 'Dupla Chance' não encontrado para {home} vs {away}")
                            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                            continue
                        
                        # Clica no botão para expandir a seção de Dupla Chance
                        try:
                            # Tenta clicar diretamente sem scroll (botão está dentro do modal)
                            page.wait_for_timeout(1000)
                            try:
                                # Tenta dispatcheventar um click diretamente
                                dc_button.dispatch_event("click")
                                logger.info(f"✅ Clicou no botão 'Dupla Chance' (dispatch_event)")
                            except Exception as dispatch_err:
                                # Fallback: force click
                                logger.info(f"DEBUG: dispatch falhou, tentando force click...")
                                dc_button.click(force=True, no_wait_after=True, timeout=3000)
                                logger.info(f"✅ Clicou no botão 'Dupla Chance' (force)")
                                
                            page.wait_for_timeout(2500)  # Aguarda seção expandir
                        except Exception as click_err:
                            logger.warning(f"⚠️ Erro ao clicar em 'Dupla Chance': {str(click_err)[:100]}")
                            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                            continue
                        
                        # Agora procura pela seção expandida com as odds
                        # Baseado no HTML: <div class="modul-accordion bet-type-group open">
                        dc_section = None
                        try:
                            # Debug: conta elementos com diferentes seletores
                            count_open = page.locator("div.bet-type-group.open").count()
                            count_bet_type = page.locator("div.bet-type-group").count()  
                            count_modul = page.locator("div.modul-accordion").count()
                            count_bet_btn = page.locator("a.bet-btn").count()
                            
                            logger.info(f"DEBUG: div.bet-type-group.open: {count_open}, div.bet-type-group: {count_bet_type}, div.modul-accordion: {count_modul}, a.bet-btn: {count_bet_btn}")
                            
                            # Salva HTML após click no Dupla Chance
                            try:
                                html_after_dc = page.content()
                                debug_file_dc = f"/app/storage/debug/esportes_after_dupla_chance_{i}.html"
                                with open(debug_file_dc, "w", encoding="utf-8") as f:
                                    f.write(html_after_dc)
                                logger.info(f"DEBUG: HTML após Dupla Chance salvo em {debug_file_dc}")
                            except Exception as save_err:
                                logger.warning(f"Erro ao salvar HTML pós-DC: {save_err}")
                            
                            # Tenta diferentes seletores
                            if count_open > 0:
                                dc_section = page.locator("div.bet-type-group.open").first
                                logger.info("✅ Seção encontrada com: div.bet-type-group.open")
                            elif count_bet_type > 0:
                                dc_section = page.locator("div.bet-type-group").first
                                logger.info("✅ Seção encontrada com: div.bet-type-group (sem .open)")
                            elif count_modul > 0:
                                dc_section = page.locator("div.modul-accordion").first
                                logger.info("✅ Seção encontrada com: div.modul-accordion")
                            else:
                                raise Exception("Nenhum seletor funcionou")
                                
                        except Exception as section_err:
                            logger.warning(f"⚠️ Seção expandida não encontrada para {home} vs {away}: {str(section_err)[:80]}")
                            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                            continue
                        
                        # Extrai os botões de apostas
                        # Baseado no HTML: <a bet-button="" class="... btn bet-btn ..." title="Casa Ou Empate">
                        # As odds de Dupla Chance estão na página principal após clicar na aba, não dentro da seção
                        
                        # Procura diretamente pelos botões de Dupla Chance na página
                        dc_odds_buttons = []
                        try:
                            # Procura por botões com os títulos específicos de Dupla Chance
                            casa_empate = page.locator('a.bet-btn[title*="Casa Ou Empate"]').first
                            casa_fora = page.locator('a.bet-btn[title*="Casa Ou Fora"]').first
                            empate_fora = page.locator('a.bet-btn[title*="Empate Ou Fora"]').first
                            
                            if casa_empate.count() > 0 and casa_fora.count() > 0 and empate_fora.count() > 0:
                                dc_odds_buttons = [casa_empate, casa_fora, empate_fora]
                                logger.info(f"✅ Encontrados 3 botões de Dupla Chance")
                            else:
                                logger.warning(f"⚠️ Botões de Dupla Chance não encontrados (disponíveis: casa_empate={casa_empate.count()}, casa_fora={casa_fora.count()}, empate_fora={empate_fora.count()})")
                                page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                                continue
                        except Exception as btn_err:
                            logger.warning(f"⚠️ Erro ao buscar botões de Dupla Chance: {str(btn_err)[:100]}")
                            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                            continue
                        
                        if len(dc_odds_buttons) < 3:
                            logger.warning(f"⚠️ Apenas {len(dc_odds_buttons)} odds encontradas, esperava 3")
                            page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                            continue
                        
                        dc_odds = {}
                        for btn in dc_odds_buttons:
                            try:
                                # Extrai o título do botão (title attribute)
                                title = btn.get_attribute("title")
                                if title:
                                    title = title.strip()
                                
                                # Extrai a odd (valor numérico)
                                odd_elem = btn.locator("span.bet-btn-odd")
                                if odd_elem.count() > 0:
                                    odd_text = odd_elem.inner_text().strip()
                                    try:
                                        odd_value = float(odd_text)
                                        
                                        # Mapeia título para chave do dicionário
                                        if "Casa Ou Empate" in title:
                                            dc_odds["home_draw"] = odd_value
                                            logger.debug(f"  1X (Casa ou Empate): {odd_value}")
                                        elif "Casa Ou Fora" in title:
                                            dc_odds["home_away"] = odd_value
                                            logger.debug(f"  12 (Casa ou Fora): {odd_value}")
                                        elif "Empate Ou Fora" in title:
                                            dc_odds["draw_away"] = odd_value
                                            logger.debug(f"  X2 (Empate ou Fora): {odd_value}")
                                        
                                    except ValueError:
                                        logger.warning(f"⚠️ Valor inválido para odd: {odd_text}")
                            except Exception as e:
                                logger.warning(f"⚠️ Erro ao processar botão: {str(e)[:80]}")
                                continue
                        
                        if len(dc_odds) == 3:
                            match_data = {
                                "source": "esportesdasorte",
                                "sport": "Futebol",
                                "competition": "Brasileirão Série A",
                                "event": {
                                    "id": f"eds_{home.lower().replace(' ', '_')}_{away.lower().replace(' ', '_')}",
                                    "name": f"{home} vs {away}",
                                    "start_time": None,
                                    "status": "upcoming"
                                },
                                "market": {
                                    "type": "Double Chance",
                                    "name": "Dupla Hipótese",
                                    "selections": [
                                        {"key": k, "name": k, "odd": v}
                                        for k, v in dc_odds.items()
                                    ]
                                },
                                "collected_at": datetime.utcnow().isoformat() + "Z"
                            }
                            odds_data.append(match_data)
                            logger.info(f"✅ Coletado: {home} vs {away} - {dc_odds}")
                        else:
                            logger.warning(f"⚠️ Odds incompletas: {dc_odds} (esperava 3, encontrou {len(dc_odds)})")
                    
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar Dupla Chance: {str(e)[:100]}")
                    
                    # Volta para lista principal
                    page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(1500)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar jogo {i+1}: {str(e)[:100]}")
                    # Tenta voltar para a página principal
                    try:
                        page.goto(ESPORTESDASORTE_URL, timeout=60000, wait_until="domcontentloaded")
                        page.wait_for_timeout(1000)
                    except:
                        pass
            
            logger.info(f"🎯 Total coletado: {len(odds_data)} jogos")
            return odds_data
            
        except Exception as e:
            logger.error(f"❌ Erro fatal: {str(e)}")
            return []
        finally:
            browser.close()
