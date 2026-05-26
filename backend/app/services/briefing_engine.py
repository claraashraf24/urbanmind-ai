from collections import Counter
from app.models.city_alert import CityAlert


def format_source(source: str) -> str:
    if source == "open-meteo":
        return "weather"
    if source == "ttc-gtfs-realtime":
        return "TTC transit"
    if source == "toronto-road-restrictions":
        return "road restrictions"
    return source.replace("-", " ")


def format_category(category: str) -> str:
    return category.replace("_", " ")


def generate_city_briefing(alerts: list[CityAlert]) -> dict:
    active_alerts = [alert for alert in alerts if alert.status == "active"]

    if not active_alerts:
        return {
            "headline": "Toronto is currently stable.",
            "summary": "UrbanMind AI is not detecting active high-impact city risks right now.",
            "key_drivers": [],
            "recommended_actions": [
                "Continue routine monitoring.",
                "Refresh ingestion periodically to detect new incidents.",
            ],
            "risk_level": "stable",
        }

    total_alerts = len(active_alerts)
    critical_alerts = [alert for alert in active_alerts if alert.severity == "critical"]
    high_alerts = [alert for alert in active_alerts if alert.severity == "high"]

    avg_risk = sum(alert.risk_score or 0 for alert in active_alerts) / total_alerts

    category_counts = Counter(alert.category for alert in active_alerts)
    source_counts = Counter(alert.source for alert in active_alerts)

    dominant_category = category_counts.most_common(1)[0][0]
    dominant_source = source_counts.most_common(1)[0][0]

    top_alerts = sorted(
        active_alerts,
        key=lambda alert: alert.risk_score or 0,
        reverse=True,
    )[:5]

    if avg_risk >= 85 or len(critical_alerts) >= 20:
        risk_level = "high strain"
        headline = "Toronto is operating under high urban strain."
    elif avg_risk >= 70 or len(critical_alerts) >= 5:
        risk_level = "elevated"
        headline = "Toronto is experiencing elevated city disruption risk."
    elif avg_risk >= 50:
        risk_level = "moderate"
        headline = "Toronto is showing moderate operational risk."
    else:
        risk_level = "stable"
        headline = "Toronto is currently stable with limited disruption risk."

    key_drivers = [
        f"{format_category(dominant_category).title()} is the dominant risk category.",
        f"The largest data source contributing to risk is {format_source(dominant_source)}.",
        f"There are {len(critical_alerts)} critical alerts and {len(high_alerts)} high-risk alerts.",
    ]

    for alert in top_alerts[:3]:
        key_drivers.append(
            f"High-priority alert: {alert.title} with risk score {round(alert.risk_score or 0)}/100."
        )

    recommended_actions = []

    if dominant_category == "traffic":
        recommended_actions.extend(
            [
                "Prioritize monitoring of affected road corridors and nearby congestion risk.",
                "Review high-risk road restrictions for possible multi-day disruptions.",
            ]
        )

    if dominant_category == "transit" or any(alert.category == "transit" for alert in active_alerts):
        recommended_actions.append(
            "Monitor TTC service disruptions and detours that may increase commuter delays."
        )

    if any(alert.category == "weather" for alert in active_alerts):
        recommended_actions.append(
            "Review weather-driven risk conditions and watch for secondary traffic impacts."
        )

    recommended_actions.append(
        "Use hotspot zones to focus operational attention on dense clusters of critical alerts."
    )

    return {
        "headline": headline,
        "summary": (
            f"UrbanMind AI is monitoring {total_alerts} active alerts. "
            f"The average risk score is {round(avg_risk, 2)}/100. "
            f"The dominant category is {dominant_category}, mainly driven by {format_source(dominant_source)}."
        ),
        "key_drivers": key_drivers,
        "recommended_actions": recommended_actions,
        "risk_level": risk_level,
        "total_alerts": total_alerts,
        "critical_alerts": len(critical_alerts),
        "high_alerts": len(high_alerts),
        "average_risk_score": round(avg_risk, 2),
    }