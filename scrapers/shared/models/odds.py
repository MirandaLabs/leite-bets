from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    FINISHED = "finished"


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
    status: EventStatus = EventStatus.UPCOMING


class Odds(BaseModel):
    source: str           # betano | bet365
    sport: str            # football
    competition: str      # brasileirao-serie-a
    event: Event
    market: Market
    collected_at: datetime
