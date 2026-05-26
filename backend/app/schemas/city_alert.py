from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class CityAlertCreate(BaseModel):
    title: str
    category: str
    severity: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    source: str = "system"
    risk_score: float = 0.0
    raw_payload: Optional[dict[str, Any]] = None
    external_id: Optional[str] = None
    status: str = "active"


class CityAlertResponse(CityAlertCreate):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    risk_score: float = 0.0

    class Config:
        from_attributes = True