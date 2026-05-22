from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.city_alert import CityAlert
from app.schemas.city_alert import CityAlertCreate, CityAlertResponse
from app.services.risk_engine import calculate_risk_score
from app.websocket.connection_manager import manager

router = APIRouter(
    prefix="/api/alerts",
    tags=["City Alerts"]
)


@router.post("/", response_model=CityAlertResponse)
async def create_alert(alert: CityAlertCreate, db: Session = Depends(get_db)):
    data = alert.model_dump()
    data["risk_score"] = calculate_risk_score(
        data["category"],
        data["severity"]
    )

    new_alert = CityAlert(**data)
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    await manager.broadcast({
    "id": new_alert.id,
    "title": new_alert.title,
    "category": new_alert.category,
    "severity": new_alert.severity,
    "latitude": new_alert.latitude,
    "longitude": new_alert.longitude,
    "description": new_alert.description,
    "source": new_alert.source,
    "risk_score": new_alert.risk_score,
    "created_at": str(new_alert.created_at),
})
    return new_alert


@router.get("/", response_model=List[CityAlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(CityAlert).order_by(CityAlert.created_at.desc()).all()