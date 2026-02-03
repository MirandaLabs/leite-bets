from sqlalchemy import create_engine, Column, String, DECIMAL, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Garante que usa psycopg3 (não psycopg2)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Event(Base):
    __tablename__ = "events"
    
    id = Column(String(50), primary_key=True)
    sport = Column(String(50), nullable=False)
    league = Column(String(100), nullable=False)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    event_date = Column(TIMESTAMP, nullable=False)
    status = Column(String(20), default="upcoming")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    finished_at = Column(TIMESTAMP)
    
    odds = relationship("Odd", back_populates="event", cascade="all, delete-orphan")

class Odd(Base):
    __tablename__ = "odds"
    
    id = Column(String(50), primary_key=True)
    event_id = Column(String(50), ForeignKey("events.id"))
    bookmaker = Column(String(50), nullable=False)
    market = Column(String(50), default="Resultado Final")
    home_odd = Column(DECIMAL(10, 2))
    draw_odd = Column(DECIMAL(10, 2))
    away_odd = Column(DECIMAL(10, 2))
    home_or_draw_odd = Column(DECIMAL(10, 2))  
    away_or_draw_odd = Column(DECIMAL(10, 2)) 
    scraped_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    event = relationship("Event", back_populates="odds")

class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"
    
    id = Column(String(50), primary_key=True)
    event_id = Column(String(50), ForeignKey("events.id"))
    user_bookmaker = Column(String(50), nullable=False)
    user_team = Column(String(50), nullable=False)
    user_odd = Column(DECIMAL(10, 2), nullable=False)
    hedge_bookmaker = Column(String(50), nullable=False)
    hedge_team = Column(String(50), nullable=False)
    hedge_odd = Column(DECIMAL(10, 2), nullable=False)
    profit_percent = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP)

class UserRequest(Base):
    __tablename__ = "user_requests"
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    event_id = Column(String(50), ForeignKey("events.id"))
    selected_team = Column(String(50), nullable=False)
    bookmaker = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()