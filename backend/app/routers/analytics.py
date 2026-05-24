from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.city_alert import CityAlert


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def get_city_overview(db: Session = Depends(get_db)):
    alerts = db.query(CityAlert).all()

    if not alerts:
        return {
            "urban_risk_index": 0,
            "critical_alerts": 0,
            "dominant_category": "none",
            "city_status": "stable",
        }

    total_alerts = len(alerts)

    critical_alerts = sum(1 for alert in alerts if alert.severity == "critical")
    high_alerts = sum(1 for alert in alerts if alert.severity == "high")
    medium_alerts = sum(1 for alert in alerts if alert.severity == "medium")

    avg_risk_score = sum(alert.risk_score or 0 for alert in alerts) / total_alerts

    category_counts = (
        db.query(CityAlert.category, func.count(CityAlert.id))
        .group_by(CityAlert.category)
        .order_by(func.count(CityAlert.id).desc())
        .all()
    )

    dominant_category = category_counts[0][0] if category_counts else "none"

    strain_score = min(
        100,
        round(
            avg_risk_score * 0.6
            + critical_alerts * 1.5
            + high_alerts * 0.5
            + medium_alerts * 0.1
        ),
    )

    if strain_score >= 80:
        city_status = "high strain"
    elif strain_score >= 60:
        city_status = "elevated"
    elif strain_score >= 35:
        city_status = "moderate"
    else:
        city_status = "stable"

    return {
        "urban_risk_index": strain_score,
        "critical_alerts": critical_alerts,
        "dominant_category": dominant_category,
        "city_status": city_status,
    }

@router.get("/source-distribution")
def get_source_distribution(db: Session = Depends(get_db)):
    results = (
        db.query(CityAlert.source, func.count(CityAlert.id))
        .group_by(CityAlert.source)
        .order_by(func.count(CityAlert.id).desc())
        .all()
    )

    return [
        {
            "source": source,
            "count": count,
        }
        for source, count in results
    ]


@router.get("/category-distribution")
def get_category_distribution(db: Session = Depends(get_db)):
    results = (
        db.query(CityAlert.category, func.count(CityAlert.id))
        .group_by(CityAlert.category)
        .order_by(func.count(CityAlert.id).desc())
        .all()
    )

    return [
        {
            "category": category,
            "count": count,
        }
        for category, count in results
    ]


@router.get("/top-risk-alerts")
def get_top_risk_alerts(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(CityAlert)
        .order_by(CityAlert.risk_score.desc(), CityAlert.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": alert.id,
            "title": alert.title,
            "category": alert.category,
            "severity": alert.severity,
            "source": alert.source,
            "risk_score": alert.risk_score,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]


@router.get("/district-risk")
def get_district_risk(db: Session = Depends(get_db)):
    alerts = (
        db.query(CityAlert)
        .filter(CityAlert.source == "toronto-road-restrictions")
        .all()
    )

    district_stats = {}

    for alert in alerts:
        raw = alert.raw_payload or {}
        district = raw.get("District") or "Unknown"

        if district not in district_stats:
            district_stats[district] = {
                "district": district,
                "count": 0,
                "critical_alerts": 0,
                "average_risk_score": 0,
                "total_risk_score": 0,
            }

        district_stats[district]["count"] += 1
        district_stats[district]["total_risk_score"] += alert.risk_score or 0

        if alert.severity == "critical":
            district_stats[district]["critical_alerts"] += 1

    for district in district_stats.values():
        district["average_risk_score"] = round(
            district["total_risk_score"] / district["count"], 2
        )
        del district["total_risk_score"]

    return sorted(
        district_stats.values(),
        key=lambda item: item["average_risk_score"],
        reverse=True,
    )


@router.get("/risk-summary")
def get_risk_summary(db: Session = Depends(get_db)):
    total_alerts = db.query(CityAlert).count()

    if total_alerts == 0:
        return {
            "summary": "No active alerts are currently stored.",
            "total_alerts": 0,
        }

    critical_count = (
        db.query(CityAlert)
        .filter(CityAlert.severity == "critical")
        .count()
    )

    high_count = (
        db.query(CityAlert)
        .filter(CityAlert.severity == "high")
        .count()
    )

    top_source = (
        db.query(CityAlert.source, func.count(CityAlert.id))
        .group_by(CityAlert.source)
        .order_by(func.count(CityAlert.id).desc())
        .first()
    )

    top_category = (
        db.query(CityAlert.category, func.count(CityAlert.id))
        .group_by(CityAlert.category)
        .order_by(func.count(CityAlert.id).desc())
        .first()
    )

    average_risk = (
        db.query(func.avg(CityAlert.risk_score))
        .scalar()
    )

    return {
        "summary": (
            f"UrbanMind AI is monitoring {total_alerts} active city alerts. "
            f"The dominant source is {top_source[0] if top_source else 'unknown'}, "
            f"and the dominant category is {top_category[0] if top_category else 'unknown'}. "
            f"There are {critical_count} critical alerts and {high_count} high-risk alerts. "
            f"The average risk score is {round(average_risk or 0, 2)}/100."
        ),
        "total_alerts": total_alerts,
        "critical_alerts": critical_count,
        "high_alerts": high_count,
        "top_source": top_source[0] if top_source else None,
        "top_category": top_category[0] if top_category else None,
        "average_risk_score": round(average_risk or 0, 2),
    }