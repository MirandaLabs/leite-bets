from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uvicorn
import uuid

from models import get_db, Event, Odd

app = FastAPI(
    title="Betting Bot API",
    description="API para arbitragem de apostas",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class OddsUpdate(BaseModel):
    eventId: str
    sport: str
    league: str
    homeTeam: str
    awayTeam: str
    eventDate: str
    bookmaker: str
    homeOdd: float
    drawOdd: Optional[float] = None
    awayOdd: float
    homeOrDrawOdd: Optional[float] = None 
    awayOrDrawOdd: Optional[float] = None  

@app.get("/")
def read_root():
    return {"message": "Betting Bot API", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/odds/update")
def update_odds(odds_data: OddsUpdate, db: Session = Depends(get_db)):
    """
    Endpoint para o scraper enviar as odds coletadas
    """
    try:
        # Verifica se o evento já existe
        event = db.query(Event).filter(Event.id == odds_data.eventId).first()
        
        if not event:
            # Cria o evento
            event = Event(
                id=odds_data.eventId,
                sport=odds_data.sport,
                league=odds_data.league,
                home_team=odds_data.homeTeam,
                away_team=odds_data.awayTeam,
                event_date=datetime.fromisoformat(odds_data.eventDate.replace('Z', '+00:00')),
                status="upcoming"
            )
            db.add(event)
            db.commit()
        
        # Cria a odd
        odd = Odd(
            id=f"odd_{uuid.uuid4().hex[:12]}",
            event_id=odds_data.eventId,
            bookmaker=odds_data.bookmaker,
            home_odd=odds_data.homeOdd,
            draw_odd=odds_data.drawOdd,
            away_odd=odds_data.awayOdd,
            home_or_draw_odd=odds_data.homeOrDrawOdd,  # NOVO
            away_or_draw_odd=odds_data.awayOrDrawOdd,  # NOVO
            scraped_at=datetime.utcnow()
        )

        db.add(odd)
        db.commit()
        
        return {
            "success": True,
            "message": "Odds atualizadas com sucesso",
            "eventId": odds_data.eventId,
            "bookmaker": odds_data.bookmaker
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar odds: {str(e)}")
    
    # Schema para o formato do scraper
class ScraperSelection(BaseModel):
    key: str
    name: str
    odd: float

class ScraperMarket(BaseModel):
    type: str
    name: str
    selections: list[ScraperSelection]

class ScraperEvent(BaseModel):
    id: str
    name: str
    start_time: Optional[str] = None
    status: str = "upcoming"

class ScraperOddsData(BaseModel):
    source: str
    sport: str
    competition: str
    event: ScraperEvent
    market: ScraperMarket
    collected_at: str

class ScraperPayload(BaseModel):
    data: list[ScraperOddsData]

@app.post("/api/odds/scraper")
@app.post("/api/odds/scraper")
def receive_scraper_odds(payload: ScraperPayload, db: Session = Depends(get_db)):
    """
    Endpoint específico para receber dados do scraper no formato dele
    Processa tanto '1X2' quanto 'Double Chance'
    """
    saved_count = 0
    updated_count = 0
    errors = []
    
    for odds_data in payload.data:
        try:
            # Parse do nome do evento (ex: "Grêmio vs Botafogo-RJ")
            event_name = odds_data.event.name
            teams = event_name.split(" vs ")
            
            if len(teams) != 2:
                errors.append(f"Formato inválido do evento: {event_name}")
                continue
            
            home_team = teams[0].strip()
            away_team = teams[1].strip()
            
            # Gera um eventId único baseado nos times e competição
            event_id = f"evt_{odds_data.competition}_{home_team.lower().replace(' ', '_')}_{away_team.lower().replace(' ', '_')}"
            
            # Verifica se o evento já existe
            event = db.query(Event).filter(Event.id == event_id).first()
            
            if not event:
                # Cria o evento
                event_date = datetime.fromisoformat(odds_data.event.start_time.replace('Z', '+00:00')) if odds_data.event.start_time else datetime.utcnow()
                
                # Determina o status baseado no horário
                status = odds_data.event.status if odds_data.event.status else "upcoming"
                
                event = Event(
                    id=event_id,
                    sport="Futebol",
                    league=odds_data.competition,
                    home_team=home_team,
                    away_team=away_team,
                    event_date=event_date,
                    status=status
                )
                db.add(event)
                db.commit()
            
            # Verifica se já existe odd desse bookmaker para esse evento
            existing_odd = db.query(Odd).filter(
                Odd.event_id == event_id,
                Odd.bookmaker == odds_data.source
            ).first()
            
            # Processa baseado no tipo de market
            if odds_data.market.type == "1X2":
                # Extrai as odds de Resultado Final
                home_odd = None
                draw_odd = None
                away_odd = None
                
                for selection in odds_data.market.selections:
                    if selection.key == "1" or selection.name == "Home":
                        home_odd = selection.odd
                    elif selection.key == "X" or selection.name == "Draw":
                        draw_odd = selection.odd
                    elif selection.key == "2" or selection.name == "Away":
                        away_odd = selection.odd
                
                if existing_odd:
                    # Atualiza odds de Resultado Final
                    existing_odd.home_odd = home_odd
                    existing_odd.draw_odd = draw_odd
                    existing_odd.away_odd = away_odd
                    existing_odd.scraped_at = datetime.fromisoformat(odds_data.collected_at.replace('Z', '+00:00'))
                    db.commit()
                    updated_count += 1
                else:
                    # Cria nova odd
                    odd = Odd(
                        id=f"odd_{uuid.uuid4().hex[:12]}",
                        event_id=event_id,
                        bookmaker=odds_data.source,
                        market="Resultado Final",
                        home_odd=home_odd,
                        draw_odd=draw_odd,
                        away_odd=away_odd,
                        home_or_draw_odd=None,
                        away_or_draw_odd=None,
                        scraped_at=datetime.fromisoformat(odds_data.collected_at.replace('Z', '+00:00'))
                    )
                    db.add(odd)
                    db.commit()
                    saved_count += 1
            
            elif odds_data.market.type == "Double Chance":
                # Extrai as odds de Double Chance
                home_or_draw_odd = None
                away_or_draw_odd = None
                
                for selection in odds_data.market.selections:
                    if selection.key == "1X":
                        home_or_draw_odd = selection.odd
                    elif selection.key == "X2":
                        away_or_draw_odd = selection.odd
                
                if existing_odd:
                    # Atualiza odds de Double Chance
                    existing_odd.home_or_draw_odd = home_or_draw_odd
                    existing_odd.away_or_draw_odd = away_or_draw_odd
                    existing_odd.scraped_at = datetime.fromisoformat(odds_data.collected_at.replace('Z', '+00:00'))
                    db.commit()
                    updated_count += 1
                else:
                    # Cria nova odd só com Double Chance
                    odd = Odd(
                        id=f"odd_{uuid.uuid4().hex[:12]}",
                        event_id=event_id,
                        bookmaker=odds_data.source,
                        market="Double Chance",
                        home_odd=None,
                        draw_odd=None,
                        away_odd=None,
                        home_or_draw_odd=home_or_draw_odd,
                        away_or_draw_odd=away_or_draw_odd,
                        scraped_at=datetime.fromisoformat(odds_data.collected_at.replace('Z', '+00:00'))
                    )
                    db.add(odd)
                    db.commit()
                    saved_count += 1
            
        except Exception as e:
            errors.append(f"Erro ao processar {odds_data.event.name}: {str(e)}")
            db.rollback()
    
    return {
        "success": True,
        "saved": saved_count,
        "updated": updated_count,
        "total": len(payload.data),
        "errors": errors if errors else None
    }

@app.get("/api/events")
def get_events(db: Session = Depends(get_db)):
    """
    Retorna todos os eventos disponíveis com suas odds
    Filtra apenas eventos que não estão finalizados
    """
    events = db.query(Event).filter(
        Event.status.in_(["upcoming", "live"])
    ).all()
    
    result = []
    for event in events:
        odds = db.query(Odd).filter(Odd.event_id == event.id).all()
        
        odds_by_bookmaker = {}
        for odd in odds:
            odds_by_bookmaker[odd.bookmaker] = {
                "homeOdd": float(odd.home_odd) if odd.home_odd else None,
                "drawOdd": float(odd.draw_odd) if odd.draw_odd else None,
                "awayOdd": float(odd.away_odd) if odd.away_odd else None,
                "homeOrDrawOdd": float(odd.home_or_draw_odd) if odd.home_or_draw_odd else None,
                "awayOrDrawOdd": float(odd.away_or_draw_odd) if odd.away_or_draw_odd else None
            }
        
        result.append({
            "eventId": event.id,
            "homeTeam": event.home_team,
            "awayTeam": event.away_team,
            "league": event.league,
            "eventDate": event.event_date.isoformat(),
            "odds": odds_by_bookmaker
        })
    
    return {"events": result}

# Duração média de um jogo de futebol (em minutos)
MATCH_DURATION = 120

@app.post("/api/events/update-status")
def update_event_statuses(db: Session = Depends(get_db)):
    """
    Atualiza o status de todos os eventos baseado no horário atual
    """
    try:
        now = datetime.utcnow()
        updated_count = 0
        finished_count = 0
        
        # Busca todos os eventos que não estão finalizados
        events = db.query(Event).filter(
            Event.status.in_(["upcoming", "live"])
        ).all()
        
        for event in events:
            old_status = event.status
            
            # Determina o novo status
            if now < event.event_date:
                new_status = "upcoming"
            elif (now - event.event_date) > timedelta(minutes=MATCH_DURATION):
                new_status = "finished"
            else:
                new_status = "live"
            
            if old_status != new_status:
                event.status = new_status
                
                # Se o evento foi finalizado, marca o horário e desativa as odds
                if new_status == "finished":
                    event.finished_at = now
                    
                    # Desativa todas as odds deste evento
                    db.query(Odd).filter(
                        Odd.event_id == event.id
                    ).update({"is_active": False})
                    
                    finished_count += 1
                
                updated_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "updated": updated_count,
            "finished": finished_count,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")

@app.delete("/api/events/cleanup")
def cleanup_finished_events(days_old: int = 7, db: Session = Depends(get_db)):
    """
    Remove eventos finalizados há mais de X dias
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Busca eventos finalizados há mais de X dias
        old_events = db.query(Event).filter(
            Event.status == "finished",
            Event.finished_at < cutoff_date
        ).all()
        
        deleted_count = len(old_events)
        
        for event in old_events:
            db.delete(event)
        
        db.commit()
        
        return {
            "success": True,
            "deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao limpar eventos: {str(e)}")

@app.post("/api/trigger/all")
def trigger_all_scrapers():
    """
    Endpoint para N8N: Triggera todos os scrapers de uma vez.
    Retorna resultado consolidado.
    """
    from datetime import datetime
    import os
    
    # URL do serviço scraper (variável de ambiente)
    scraper_base_url = os.getenv("SCRAPER_API_URL", "http://localhost:8001")
    
    results = {
        "triggered_at": datetime.utcnow().isoformat(),
        "scraper_url": scraper_base_url,
        "scrapers": {}
    }
    
    # Lista de scrapers disponíveis
    scrapers = {
        "betano": f"{scraper_base_url}/scrape/betano",
        "bet365": f"{scraper_base_url}/scrape/bet365",
        "superbet": f"{scraper_base_url}/scrape/superbet",
        "esportesdasorte": f"{scraper_base_url}/scrape/esportesdasorte"
    }
    
    import requests
    
    for name, url in scrapers.items():
        try:
            response = requests.post(url, timeout=60)
            results["scrapers"][name] = {
                "status": "success",
                "status_code": response.status_code,
                "items": response.json().get("items", 0)
            }
        except Exception as e:
            results["scrapers"][name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


@app.post("/api/trigger/{casa}")
def trigger_scraper_casa(casa: str):
    """
    Endpoint para N8N: Triggera scraper específico.
    Casas disponíveis: betano, bet365, superbet, esportesdasorte
    """
    from datetime import datetime
    import requests
    import os
    
    # URL do serviço scraper (variável de ambiente)
    scraper_base_url = os.getenv("SCRAPER_API_URL", "http://localhost:8001")
    
    scrapers = {
        "betano": f"{scraper_base_url}/scrape/betano",
        "bet365": f"{scraper_base_url}/scrape/bet365",
        "superbet": f"{scraper_base_url}/scrape/superbet",
        "esportesdasorte": f"{scraper_base_url}/scrape/esportesdasorte"
    }
    
    if casa not in scrapers:
        return {
            "error": f"Casa '{casa}' não encontrada",
            "available": list(scrapers.keys())
        }
    
    try:
        response = requests.post(scrapers[casa], timeout=60)
        return {
            "triggered_at": datetime.utcnow().isoformat(),
            "casa": casa,
            "status": "success",
            "data": response.json()
        }
    except Exception as e:
        return {
            "triggered_at": datetime.utcnow().isoformat(),
            "casa": casa,
            "status": "error",
            "error": str(e)
        }


@app.get("/api/scraper/status")
def scraper_status():
    """
    Endpoint para N8N: Verifica status dos scrapers e sistema.
    """
    from datetime import datetime
    
    # Verifica banco de dados
    try:
        db = SessionLocal()
        event_count = db.query(Event).count()
        odd_count = db.query(Odd).count()
        upcoming_events = db.query(Event).filter(Event.status == "upcoming").count()
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        event_count = 0
        odd_count = 0
        upcoming_events = 0
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "events": event_count,
            "odds": odd_count,
            "upcoming_events": upcoming_events
        },
        "scrapers": {
            "available": ["betano", "bet365", "superbet", "esportesdasorte"],
            "trigger_endpoint": "/api/trigger/all"
        }
    }


@app.post("/api/webhook/n8n")
def webhook_n8n(payload: dict = None):
    """
    Webhook genérico para N8N.
    N8N pode enviar qualquer payload e este endpoint processa.
    """
    from datetime import datetime
    
    action = payload.get("action") if payload else None
    
    if action == "scrape_all":
        # Triggera todos os scrapers
        return trigger_all_scrapers()
    
    elif action == "scrape_casa":
        # Triggera scraper específico
        casa = payload.get("casa")
        if not casa:
            return {"error": "Campo 'casa' obrigatório quando action='scrape_casa'"}
        return trigger_scraper_casa(casa)
    
    elif action == "status":
        # Retorna status
        return scraper_status()
    
    else:
        return {
            "received_at": datetime.utcnow().isoformat(),
            "payload": payload,
            "available_actions": ["scrape_all", "scrape_casa", "status"],
            "message": "Webhook recebido! Use 'action' para especificar o que fazer."
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)