from pydantic import BaseModel
from typing import Optional


class ForexNews(BaseModel):
    id: str
    source: str
    timestamp: str
    currency: str
    importance: str
    event: str
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    sentiment: Optional[str] = "Pending"
