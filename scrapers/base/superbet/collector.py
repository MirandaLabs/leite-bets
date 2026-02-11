def collect():
    """Collect match odds from Superbet using Playwright with proxy rotation and auto-retry."""
    
    with sync_playwright() as p:
        # Loop de tentativas
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(f"🔄 Tentativa {attempt}/{MAX_RETRIES} para Superbet...")
            
            try:
                browser, context = get_browser_context(p, scraper_name="superbet")
                page = context.new_page()
                
                # Configura timeout maior
                page.set_default_timeout(120000)
                
                logger.info(f"Abrindo Superbet: {SUPERBET_URL}")
                
                # Navega com timeout maior e sem esperar carregamento completo
                response = page.goto(
                    SUPERBET_URL, 
                    timeout=120000,
                    wait_until="commit"  # Apenas espera o commit, não o carregamento completo
                )
                
                if not response or response.status >= 400:
                    logger.error(f"❌ Erro HTTP: {response.status if response else 'Sem resposta'}")
                    raise ValueError(f"Erro na resposta: {response.status}")
                
                # Aguarda um tempo para o conteúdo carregar
                page.wait_for_timeout(10000)  # 10 segundos
                
                # Verifica se temos conteúdo
                html = page.content()
                logger.info(f"HTML obtido: {len(html)} bytes")
                
                if len(html) < 10000:  # Aumentei o limite mínimo
                    logger.warning("⚠️ HTML muito pequeno, possível bloqueio")
                    raise ValueError("HTML insuficiente")
                
                # Tenta localizar elementos chave
                try:
                    page.wait_for_selector("div.event-card", timeout=30000)
                except:
                    # Tenta alternativa
                    page.wait_for_selector("div[class*='event']", timeout=30000)
                
                # Tira screenshot para debug
                try:
                    os.makedirs("storage/debug", exist_ok=True)
                    page.screenshot(path=f"storage/debug/superbet_attempt_{attempt}.png")
                except:
                    pass
                
                # Extrai dados
                final_html = page.content()
                matches = parse_matchresult_from_main_page(final_html)
                
                if matches:
                    logger.info(f"✅ Sucesso! Coletados {len(matches)} jogos")
                    browser.close()
                    return matches
                else:
                    raise ValueError("Nenhum jogo coletado")
                    
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {attempt}: {str(e)}")
                
                # Fecha o browser se existir
                try:
                    browser.close()
                except:
                    pass
                
                if attempt == MAX_RETRIES:
                    raise ScraperError(f"Falha na Superbet após {MAX_RETRIES} tentativas")
                
                logger.info(f"Aguardando 5 segundos antes da próxima tentativa...")
                time.sleep(5)