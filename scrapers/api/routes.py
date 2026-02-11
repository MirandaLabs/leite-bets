from fastapi import APIRouter
from scrapers.workflows.run_bet365 import run as run_bet365
from scrapers.workflows.run_betano import run as run_betano
from scrapers.workflows.run_superbet import run as run_superbet
from scrapers.workflows.run_esportesdasorte import run as run_esportesdasorte
from scrapers.base.betano.collector import collect as collect_betano_raw
from playwright.sync_api import sync_playwright
import logging

# Configuração de logs
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/debug/betano-html")
def debug_betano_html():
    """Debug endpoint to check what HTML is being retrieved from Betano."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
            context = browser.new_context(
                locale="pt-BR",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto("https://br.betano.com", timeout=30000)
            content = page.content()
            browser.close()
            return {"html_length": len(content), "preview": content[:500]}
    except Exception as e:
        return {"error": str(e)}

@router.post("/scrape/bet365")
def scrape_bet365():
    try:
        data = run_bet365()
        return {
            "source": "bet365",
            "items": len(data),
            "data": data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro no scrape_bet365: {e}")
        return {"source": "bet365", "status": "error", "message": str(e)}

@router.post("/scrape/betano")
def scrape_betano():
    try:
        data = run_betano()
        return {
            "source": "betano",
            "items": len(data),
            "data": data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro no scrape_betano: {e}")
        return {"source": "betano", "status": "error", "message": str(e)}

@router.post("/scrape/superbet")
def scrape_superbet():
    try:
        data = run_superbet()
        return {
            "source": "superbet",
            "items": len(data),
            "data": data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro no scrape_superbet: {e}")
        return {"source": "superbet", "status": "error", "message": str(e)}

@router.post("/scrape/esportesdasorte")
def scrape_esportesdasorte():
    try:
        data = run_esportesdasorte()
        return {
            "source": "esportesdasorte",
            "items": len(data),
            "data": data,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro no scrape_esportesdasorte: {e}")
        return {"source": "esportesdasorte", "status": "error", "message": str(e)}

# --- NOVA ROTA QUE FALTAVA ---
@router.post("/api/trigger/all")
def trigger_all():
    """Executa todos os scrapers sequencialmente e retorna um relatório consolidado."""
    report = {}
    
    # 1. Betano
    try:
        logger.info("Iniciando Betano via Trigger All...")
        betano_data = run_betano()
        report["betano"] = {"status": "success", "items": len(betano_data)}
    except Exception as e:
        logger.error(f"Falha Betano: {e}")
        report["betano"] = {"status": "error", "message": str(e)}

    # 2. Bet365
    try:
        logger.info("Iniciando Bet365 via Trigger All...")
        bet365_data = run_bet365()
        report["bet365"] = {"status": "success", "items": len(bet365_data)}
    except Exception as e:
        logger.error(f"Falha Bet365: {e}")
        report["bet365"] = {"status": "error", "message": str(e)}

    # 3. Superbet
    try:
        logger.info("Iniciando Superbet via Trigger All...")
        superbet_data = run_superbet()
        report["superbet"] = {"status": "success", "items": len(superbet_data)}
    except Exception as e:
        logger.error(f"Falha Superbet: {e}")
        report["superbet"] = {"status": "error", "message": str(e)}

    # 4. Esportes da Sorte
    try:
        logger.info("Iniciando Esportes da Sorte via Trigger All...")
        esportes_data = run_esportesdasorte()
        report["esportesdasorte"] = {"status": "success", "items": len(esportes_data)}
    except Exception as e:
        logger.error(f"Falha Esportes da Sorte: {e}")
        report["esportesdasorte"] = {"status": "error", "message": str(e)}

    return {
        "message": "Ciclo de scraping finalizado",
        "scrapers": report
    }

# --- ROTA PARA SCRAPERS LOCAIS (SEM PROXY) ---
@router.post("/api/trigger/local")
def trigger_local():
    """Executa scrapers locais sem proxy (para ambiente de desenvolvimento)."""
    from datetime import datetime
    import traceback
    
    logger.info("=" * 80)
    logger.info("🏠 INICIANDO COLETA LOCAL (SEM PROXY)")
    logger.info("=" * 80)
    
    report = {
        "triggered_at": datetime.utcnow().isoformat() + "Z",
        "environment": "local",
        "proxy_enabled": False,
        "scrapers": {}
    }
    
    # Import local scrapers
    try:
        from scrapers.local.betano_local import collect_betano_local
        from scrapers.local.superbet_local import collect_superbet_local
        from scrapers.local.esportesdasorte_local import collect_esportesdasorte_local
        from scrapers.local.bet365_local import collect_bet365_local
        from scrapers.shared.sender import send_odds_to_api
    except ImportError as e:
        logger.error(f"❌ Erro ao importar scrapers locais: {e}")
        return {
            "status": "error",
            "message": f"Scrapers locais não encontrados: {str(e)}",
            "scrapers": {}
        }
    
    # 1. Betano Local
    try:
        logger.info("\n📊 [1/4] BETANO LOCAL")
        betano_data = collect_betano_local()
        if betano_data:
            send_status = send_odds_to_api(betano_data)
            report["scrapers"]["betano"] = {
                "status": "success",
                "items": len(betano_data),
                "sent_to_api": send_status
            }
            logger.info(f"✅ Betano: {len(betano_data)} jogos coletados")
        else:
            report["scrapers"]["betano"] = {
                "status": "warning",
                "items": 0,
                "message": "Nenhum dado coletado"
            }
            logger.warning("⚠️ Betano: Sem dados")
    except Exception as e:
        logger.error(f"❌ Erro Betano: {e}\n{traceback.format_exc()}")
        report["scrapers"]["betano"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 2. Superbet Local
    try:
        logger.info("\n📊 [2/4] SUPERBET LOCAL")
        superbet_data = collect_superbet_local()
        if superbet_data:
            send_status = send_odds_to_api(superbet_data)
            report["scrapers"]["superbet"] = {
                "status": "success",
                "items": len(superbet_data),
                "sent_to_api": send_status
            }
            logger.info(f"✅ Superbet: {len(superbet_data)} jogos coletados")
        else:
            report["scrapers"]["superbet"] = {
                "status": "warning",
                "items": 0,
                "message": "Nenhum dado coletado (parser pendente)"
            }
            logger.warning("⚠️ Superbet: Sem dados")
    except Exception as e:
        logger.error(f"❌ Erro Superbet: {e}\n{traceback.format_exc()}")
        report["scrapers"]["superbet"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 3. Esportes da Sorte Local
    try:
        logger.info("\n📊 [3/4] ESPORTES DA SORTE LOCAL")
        esportes_data = collect_esportesdasorte_local()
        if esportes_data:
            send_status = send_odds_to_api(esportes_data)
            report["scrapers"]["esportesdasorte"] = {
                "status": "success",
                "items": len(esportes_data),
                "sent_to_api": send_status
            }
            logger.info(f"✅ Esportes: {len(esportes_data)} jogos coletados")
        else:
            report["scrapers"]["esportesdasorte"] = {
                "status": "warning",
                "items": 0,
                "message": "Nenhum dado coletado"
            }
            logger.warning("⚠️ Esportes: Sem dados")
    except Exception as e:
        logger.error(f"❌ Erro Esportes: {e}\n{traceback.format_exc()}")
        report["scrapers"]["esportesdasorte"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 4. Bet365 Local
    try:
        logger.info("\n📊 [4/4] BET365 LOCAL")
        bet365_data = collect_bet365_local()
        if bet365_data:
            send_status = send_odds_to_api(bet365_data)
            report["scrapers"]["bet365"] = {
                "status": "success",
                "items": len(bet365_data),
                "sent_to_api": send_status
            }
            logger.info(f"✅ Bet365: {len(bet365_data)} jogos coletados")
        else:
            report["scrapers"]["bet365"] = {
                "status": "warning",
                "items": 0,
                "message": "Nenhum dado coletado (parser pendente)"
            }
            logger.warning("⚠️ Bet365: Sem dados")
    except Exception as e:
        logger.error(f"❌ Erro Bet365: {e}\n{traceback.format_exc()}")
        report["scrapers"]["bet365"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Resumo
    total_items = sum(
        s.get("items", 0) 
        for s in report["scrapers"].values() 
        if s.get("status") == "success"
    )
    
    logger.info("\n" + "=" * 80)
    logger.info(f"🎯 RESUMO: {total_items} jogos coletados no total")
    logger.info("=" * 80)
    
    report["total_items"] = total_items
    report["status"] = "success" if total_items > 0 else "warning"
    
    return report