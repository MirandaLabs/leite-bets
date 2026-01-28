from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Selection(BaseModel):
    key: str              # "1", "X", "2"
    name: str             # Home / Draw / Away
    odd: float


class Market(BaseModel):
    type: str             # "1X2"
    name: str             # "Match Result"
    selections: List[Selection]


class Event(BaseModel):
    id: str
    name: str
    start_time: Optional[datetime]
    is_live: bool


class Odds(BaseModel):
    source: str           # betano | bet365
    sport: str            # football
    competition: str      # brasileirao-serie-a
    event: Event
    market: Market
    collected_at: datetime
