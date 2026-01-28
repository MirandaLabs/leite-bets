from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
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
    is_live: bool

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
                event = Event(
                    id=event_id,
                    sport="Futebol",
                    league=odds_data.competition,
                    home_team=home_team,
                    away_team=away_team,
                    event_date=event_date,
                    status="live" if odds_data.event.is_live else "upcoming"
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)