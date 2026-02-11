"""
Script para rodar todos os scrapers localmente sem proxy
Envia dados para a API no Railway
"""
import logging
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scrapers.local.betano_local import collect_betano_local
from scrapers.local.superbet_local import collect_superbet_local
from scrapers.local.esportesdasorte_local import collect_esportesdasorte_local
from scrapers.local.bet365_local import collect_bet365_local
from scrapers.shared.sender import send_odds_to_api
from scrapers.shared.logger import setup_logger

# Carrega variáveis de ambiente do .env.local
from dotenv import load_dotenv
load_dotenv('.env.local')

logger = setup_logger("local_scraper")


def run_all_scrapers_local():
    """
    Executa todos os scrapers sequencialmente sem proxy
    Envia dados para o Railway
    """
    logger.info("=" * 80)
    logger.info("🏠 INICIANDO COLETA LOCAL (SEM PROXY)")
    logger.info("=" * 80)
    
    # Verifica API_URL
    api_url = os.getenv('API_URL')
    if not api_url:
        logger.error("❌ API_URL não configurada no .env.local!")
        return
    
    logger.info(f"📡 Enviando dados para: {api_url}")
    logger.info("")
    
    total_collected = 0
    results = {}
    
    # 1. Betano
    logger.info("\n📊 [1/4] BETANO")
    logger.info("-" * 40)
    try:
        betano_data = collect_betano_local()
        if betano_data:
            success = send_odds_to_api(betano_data)
            results["betano"] = {
                "collected": len(betano_data),
                "sent": success
            }
            total_collected += len(betano_data)
            logger.info(f"✅ Betano: {len(betano_data)} jogos coletados e enviados")
        else:
            results["betano"] = {"collected": 0, "sent": False}
            logger.warning("⚠️ Betano: Nenhum dado coletado")
    except Exception as e:
        logger.error(f"❌ Erro na Betano: {str(e)}")
        results["betano"] = {"error": str(e)}
    
    # 2. Superbet
    logger.info("\n📊 [2/4] SUPERBET")
    logger.info("-" * 40)
    try:
        superbet_data = collect_superbet_local()
        if superbet_data:
            success = send_odds_to_api(superbet_data)
            results["superbet"] = {
                "collected": len(superbet_data),
                "sent": success
            }
            total_collected += len(superbet_data)
            logger.info(f"✅ Superbet: {len(superbet_data)} jogos coletados e enviados")
        else:
            results["superbet"] = {"collected": 0, "sent": False}
            logger.warning("⚠️ Superbet: Nenhum dado coletado")
    except Exception as e:
        logger.error(f"❌ Erro na Superbet: {str(e)}")
        results["superbet"] = {"error": str(e)}
    
    # 3. Esportes da Sorte
    logger.info("\n📊 [3/4] ESPORTES DA SORTE")
    logger.info("-" * 40)
    try:
        esportes_data = collect_esportesdasorte_local()
        if esportes_data:
            success = send_odds_to_api(esportes_data)
            results["esportesdasorte"] = {
                "collected": len(esportes_data),
                "sent": success
            }
            total_collected += len(esportes_data)
            logger.info(f"✅ Esportes: {len(esportes_data)} jogos coletados e enviados")
        else:
            results["esportesdasorte"] = {"collected": 0, "sent": False}
            logger.warning("⚠️ Esportes: Nenhum dado coletado")
    except Exception as e:
        logger.error(f"❌ Erro na Esportes da Sorte: {str(e)}")
        results["esportesdasorte"] = {"error": str(e)}
    
    # 4. Bet365
    logger.info("\n📊 [4/4] BET365")
    logger.info("-" * 40)
    try:
        bet365_data = collect_bet365_local()
        if bet365_data:
            success = send_odds_to_api(bet365_data)
            results["bet365"] = {
                "collected": len(bet365_data),
                "sent": success
            }
            total_collected += len(bet365_data)
            logger.info(f"✅ Bet365: {len(bet365_data)} jogos coletados e enviados")
        else:
            results["bet365"] = {"collected": 0, "sent": False}
            logger.warning("⚠️ Bet365: Nenhum dados coletado")
    except Exception as e:
        logger.error(f"❌ Erro na Bet365: {str(e)}")
        results["bet365"] = {"error": str(e)}
    
    # Resumo final
    logger.info("\n" + "=" * 80)
    logger.info(f"🎯 RESUMO DA COLETA LOCAL")
    logger.info("=" * 80)
    logger.info(f"Total coletado: {total_collected} jogos")
    logger.info("")
    
    for casa, result in results.items():
        if "error" in result:
            logger.error(f"❌ {casa.upper()}: Erro - {result['error']}")
        elif result.get("collected", 0) > 0:
            status = "✅ Enviado" if result.get("sent") else "❌ Falha no envio"
            logger.info(f"{status} {casa.upper()}: {result['collected']} jogos")
        else:
            logger.warning(f"⚠️ {casa.upper()}: Sem dados")
    
    logger.info("=" * 80)
    
    return results


if __name__ == "__main__":
    run_all_scrapers_local()
