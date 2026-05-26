from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from math import radians, sin, cos, sqrt, atan2
from app.services.briefing_engine import generate_city_briefing

from app.database import get_db
from app.models.city_alert import CityAlert


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def get_city_overview(db: Session = Depends(get_db)):
    alerts = db.query(CityAlert).filter(CityAlert.status == "active").all()

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
        .filter(CityAlert.status == "active")
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
        .filter(CityAlert.status == "active")
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
        .filter(CityAlert.status == "active")
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

def calculate_distance_km(lat1, lon1, lat2, lon2):
    radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return radius * c

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
        .filter(CityAlert.status == "active")
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

@router.get("/risk-hotspots")
def get_risk_hotspots(
    radius_km: float = 1.0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(CityAlert)
        .filter(CityAlert.status == "active")
        .filter(CityAlert.risk_score >= 60)
        .all()
    )

    hotspots = []
    used_alert_ids = set()

    sorted_alerts = sorted(
        alerts,
        key=lambda alert: alert.risk_score or 0,
        reverse=True,
    )

    for alert in sorted_alerts:
        if alert.id in used_alert_ids:
            continue

        nearby_alerts = []

        for candidate in alerts:
            distance = calculate_distance_km(
                alert.latitude,
                alert.longitude,
                candidate.latitude,
                candidate.longitude,
            )

            if distance <= radius_km:
                nearby_alerts.append(candidate)

        if len(nearby_alerts) < 2:
            continue

        for nearby in nearby_alerts:
            used_alert_ids.add(nearby.id)

        average_latitude = sum(item.latitude for item in nearby_alerts) / len(
            nearby_alerts
        )
        average_longitude = sum(item.longitude for item in nearby_alerts) / len(
            nearby_alerts
        )

        average_risk_score = sum(
            item.risk_score or 0 for item in nearby_alerts
        ) / len(nearby_alerts)

        critical_alerts = sum(
            1 for item in nearby_alerts if item.severity == "critical"
        )

        top_alert = max(
            nearby_alerts,
            key=lambda item: item.risk_score or 0,
        )

        categories = {}
        sources = {}

        for item in nearby_alerts:
            categories[item.category] = categories.get(item.category, 0) + 1
            sources[item.source] = sources.get(item.source, 0) + 1

        dominant_category = max(categories.items(), key=lambda item: item[1])[0]
        dominant_source = max(sources.items(), key=lambda item: item[1])[0]

        hotspots.append(
            {
                "center_latitude": round(average_latitude, 6),
                "center_longitude": round(average_longitude, 6),
                "alert_count": len(nearby_alerts),
                "critical_alerts": critical_alerts,
                "average_risk_score": round(average_risk_score, 2),
                "dominant_category": dominant_category,
                "dominant_source": dominant_source,
                "top_alert_id": top_alert.id,
                "top_alert_title": top_alert.title,
                "radius_km": radius_km,
            }
        )

    hotspots = sorted(
        hotspots,
        key=lambda item: (
            item["average_risk_score"],
            item["critical_alerts"],
            item["alert_count"],
        ),
        reverse=True,
    )

    return hotspots[:limit]

@router.get("/briefing")
def get_city_briefing(db: Session = Depends(get_db)):
    alerts = (
        db.query(CityAlert)
        .filter(CityAlert.status == "active")
        .all()
    )

    return generate_city_briefing(alerts)