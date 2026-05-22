from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.city_alert import CityAlert

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/overview")
def get_city_overview(db: Session = Depends(get_db)):
    total_alerts = db.query(CityAlert).count()

    critical_alerts = db.query(CityAlert).filter(
        CityAlert.severity == "critical"
    ).count()

    average_risk_score = db.query(
        func.avg(CityAlert.risk_score)
    ).scalar() or 0

    category_counts = (
        db.query(
            CityAlert.category,
            func.count(CityAlert.category)
        )
        .group_by(CityAlert.category)
        .order_by(func.count(CityAlert.category).desc())
        .first()
    )

    dominant_category = category_counts[0] if category_counts else "none"

    if average_risk_score >= 85:
        city_status = "CRITICAL"
    elif average_risk_score >= 70:
        city_status = "HIGH STRAIN"
    elif average_risk_score >= 50:
        city_status = "ELEVATED"
    else:
        city_status = "STABLE"

    return {
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "average_risk_score": round(average_risk_score, 1),
        "dominant_category": dominant_category,
        "city_status": city_status,
    }