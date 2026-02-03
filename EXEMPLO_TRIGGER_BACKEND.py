"""
Exemplo de implementação para adicionar ao backend/main.py

Este código deve ser adicionado após os imports e antes das rotas atuais.
"""

from fastapi import BackgroundTasks, HTTPException
from datetime import datetime
import httpx
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configuração da URL do scraper
SCRAPER_API_URL = os.getenv("SCRAPER_API_URL", "http://localhost:8001")
SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "300"))  # 5 minutos

# ============================================================================
# NOVO: Endpoint para trigger dos scrapers
# ============================================================================

@app.post("/api/trigger/all")
async def trigger_all_scrapers(background_tasks: BackgroundTasks):
    """
    Trigger para todos os scrapers executarem em background.
    
    Utilidade: Chamado pelo N8N em intervalos regulares (ex: a cada 30 min)
    
    Resposta:
    {
        "status": "triggered",
        "message": "Scrapers iniciados em background",
        "timestamp": "2026-01-28T15:30:45.123456"
    }
    
    Logs: Verifique os logs da aplicação para status de cada scraper
    """
    # Executa em background para não bloquear a requisição
    background_tasks.add_task(run_all_scrapers_background)
    
    return {
        "status": "triggered",
        "message": "Scrapers iniciados em background",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Verifique os logs para acompanhar o progresso"
    }


@app.post("/api/trigger/{scraper_name}")
async def trigger_specific_scraper(
    scraper_name: str,
    background_tasks: BackgroundTasks
):
    """
    Trigger para um scraper específico.
    
    Params:
    - scraper_name: betano, bet365, superbet, esportesdasorte
    
    Exemplo:
    POST /api/trigger/betano
    """
    valid_scrapers = ["betano", "bet365", "superbet", "esportesdasorte"]
    
    if scraper_name.lower() not in valid_scrapers:
        raise HTTPException(
            status_code=400,
            detail=f"Scraper inválido. Use um de: {', '.join(valid_scrapers)}"
        )
    
    background_tasks.add_task(
        run_specific_scraper_background,
        scraper_name.lower()
    )
    
    return {
        "status": "triggered",
        "scraper": scraper_name,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/scraper/status")
def get_scraper_status(db: Session = Depends(get_db)):
    """
    Retorna status do sistema de scraping e eventos no banco.
    
    Resposta:
    {
        "status": "ok",
        "database": {
            "events": 150,
            "odds": 450,
            "upcoming_events": 120,
            "live_events": 5,
            "finished_events": 25
        },
        "last_scrape": "2026-01-28T15:30:00Z"
    }
    """
    try:
        total_events = db.query(Event).count()
        total_odds = db.query(Odd).count()
        upcoming_events = db.query(Event).filter(
            Event.status == "upcoming"
        ).count()
        live_events = db.query(Event).filter(
            Event.status == "live"
        ).count()
        finished_events = db.query(Event).filter(
            Event.status == "finished"
        ).count()
        
        # Encontra a última raspagem
        last_odd = db.query(Odd).order_by(Odd.scraped_at.desc()).first()
        last_scrape = last_odd.scraped_at if last_odd else None
        
        return {
            "status": "ok",
            "database": {
                "events": total_events,
                "odds": total_odds,
                "upcoming_events": upcoming_events,
                "live_events": live_events,
                "finished_events": finished_events
            },
            "last_scrape": last_scrape.isoformat() if last_scrape else None
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao verificar status")


# ============================================================================
# FUNÇÕES INTERNAS (executam em background)
# ============================================================================

async def run_all_scrapers_background():
    """
    Executa todos os scrapers sequencialmente em background.
    Cada scraper é chamado no serviço separado de scrapers.
    """
    results = {}
    scrapers = ["betano", "bet365", "superbet", "esportesdasorte"]
    
    logger.info("🔄 Iniciando raspagem de TODOS os sites...")
    logger.info(f"URL do Scraper API: {SCRAPER_API_URL}")
    
    async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT) as client:
        for scraper in scrapers:
            try:
                logger.info(f"📊 Triggering {scraper}...")
                
                # Chama o endpoint POST do scraper
                response = await client.post(
                    f"{SCRAPER_API_URL}/scrape/{scraper}",
                    timeout=SCRAPER_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items_count = len(data.get("data", []))
                    results[scraper] = {
                        "status": "success",
                        "items": items_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    logger.info(f"✅ {scraper}: {items_count} items coletados")
                else:
                    results[scraper] = {
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    logger.error(f"❌ {scraper}: HTTP {response.status_code}")
                    
            except httpx.TimeoutException:
                results[scraper] = {
                    "status": "error",
                    "error": "Timeout após 5 minutos",
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"❌ {scraper}: Timeout")
                
            except Exception as e:
                results[scraper] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                logger.error(f"❌ {scraper}: {str(e)}")
    
    logger.info(f"✅ Raspagem completada. Resultados: {results}")
    return results


async def run_specific_scraper_background(scraper_name: str):
    """
    Executa um scraper específico em background.
    """
    logger.info(f"🔄 Iniciando raspagem: {scraper_name}")
    
    async with httpx.AsyncClient(timeout=SCRAPER_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{SCRAPER_API_URL}/scrape/{scraper_name}",
                timeout=SCRAPER_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                items_count = len(data.get("data", []))
                logger.info(f"✅ {scraper_name}: {items_count} items coletados")
            else:
                logger.error(f"❌ {scraper_name}: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ {scraper_name}: {str(e)}")


# ============================================================================
# VARIÁVEL DE AMBIENTE NECESSÁRIA
# ============================================================================

"""
Adicione ao seu .env ou às variáveis do Railway:

SCRAPER_API_URL=https://seu-scraper-railway.railway.app
SCRAPER_TIMEOUT=300

Localmente com docker-compose, deixe o padrão:
SCRAPER_API_URL=http://scraper:8000
"""


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

"""
1. TRIGGER TODOS OS SCRAPERS:
   
   curl -X POST http://localhost:8000/api/trigger/all
   
   Resposta:
   {
     "status": "triggered",
     "message": "Scrapers iniciados em background",
     "timestamp": "2026-01-28T15:30:45.123456"
   }


2. TRIGGER SCRAPER ESPECÍFICO:
   
   curl -X POST http://localhost:8000/api/trigger/betano
   
   Resposta:
   {
     "status": "triggered",
     "scraper": "betano",
     "timestamp": "2026-01-28T15:30:45.123456"
   }


3. VERIFICAR STATUS:
   
   curl http://localhost:8000/api/scraper/status
   
   Resposta:
   {
     "status": "ok",
     "database": {
       "events": 150,
       "odds": 450,
       "upcoming_events": 120,
       "live_events": 5,
       "finished_events": 25
     },
     "last_scrape": "2026-01-28T15:30:00Z"
   }


4. NO N8N - HTTP REQUEST NODE:
   
   Method: POST
   URL: https://seu-backend-railway.railway.app/api/trigger/all
   Headers: Content-Type: application/json
   Authentication: None
   
   Intervalos recomendados:
   - 30 minutos para odds em tempo real
   - 60 minutos para economia de banda
   - 15 minutos para jogos ao vivo


5. MONITORAR LOGS NO RAILWAY:
   
   railway logs --service backend --follow
   
   Você verá:
   🔄 Iniciando raspagem de TODOS os sites...
   📊 Triggering betano...
   ✅ betano: 25 items coletados
   ...
"""
