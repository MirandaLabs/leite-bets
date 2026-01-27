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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)