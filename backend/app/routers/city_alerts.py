from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.city_alert import CityAlert
from app.schemas.city_alert import CityAlertResponse
from app.services.risk_engine import explain_risk


router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=list[CityAlertResponse])
def get_alerts(
    source: str | None = Query(default=None),
    category: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=300, ge=1, le=3000),
    db: Session = Depends(get_db),
):
    query = db.query(CityAlert)

    if source:
        query = query.filter(CityAlert.source == source)

    if category:
        query = query.filter(CityAlert.category == category)

    if severity:
        query = query.filter(CityAlert.severity == severity)

    alerts = (
        query
        .order_by(CityAlert.created_at.desc())
        .limit(limit)
        .all()
    )

    return alerts

@router.get("/{alert_id}/risk-explanation")
def get_alert_risk_explanation(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = db.query(CityAlert).filter(CityAlert.id == alert_id).first()

    if not alert:
        return {"error": "Alert not found"}

    event = {
        "source": alert.source,
        "category": alert.category,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "latitude": alert.latitude,
        "longitude": alert.longitude,
        "risk_score": alert.risk_score,
        "raw_payload": alert.raw_payload or {},
    }

    return {
        "alert_id": alert.id,
        "title": alert.title,
        "risk_score": alert.risk_score,
        "source": alert.source,
        "category": alert.category,
        "severity": alert.severity,
        "reasons": explain_risk(event),
    }