import requests
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2
from app.services.risk_engine import calculate_city_event_risk


# Start with this. If your discovery script prints a different URL, replace this.
TTC_ALERTS_URL = "https://bustime.ttc.ca/gtfsrt/alerts"


def get_text(translated_string, fallback):
    if translated_string.translation:
        return translated_string.translation[0].text
    return fallback


def classify_ttc_severity(title, description):
    text = f"{title} {description}".lower()

    critical_keywords = [
        "no subway service",
        "no service",
        "suspended",
        "closure",
        "closed",
        "not stopping",
        "shuttle buses are running",
        "emergency",
        "collision",
        "fire",
        "police investigation",
    ]

    high_keywords = [
        "delay",
        "delays",
        "detour",
        "bypass",
        "reduced speed",
        "blocked road",
        "downed electrical wire",
        "technical problem",
    ]

    low_priority_keywords = [
        "proof of payment",
        "please look both ways",
        "presto",
        "fare",
    ]

    if any(keyword in text for keyword in low_priority_keywords):
        return "low"

    if any(keyword in text for keyword in critical_keywords):
        return "critical"

    if any(keyword in text for keyword in high_keywords):
        return "high"

    return "medium"


def should_keep_ttc_alert(title, description):
    text = f"{title} {description}".lower()

    ignore_keywords = [
        "proof of payment",
        "please look both ways",
        "fare inspection",
        "have your fare",
        "customer notice",
    ]

    return not any(keyword in text for keyword in ignore_keywords)


def get_ttc_alerts():
    feed = gtfs_realtime_pb2.FeedMessage()

    response = requests.get(TTC_ALERTS_URL, timeout=30)
    response.raise_for_status()

    feed.ParseFromString(response.content)

    alerts = []

    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue

        alert = entity.alert

        title = get_text(alert.header_text, "TTC service alert")
        description = get_text(alert.description_text, "Transit disruption detected.")

        if not should_keep_ttc_alert(title, description):
            continue

        severity = classify_ttc_severity(title, description)

        event = {
            "external_id": f"ttc-{entity.id}",
            "source": "ttc-gtfs-realtime",
            "category": "transit",
            "severity": severity,
            "title": title,
            "description": description,
            "latitude": 43.6532,
            "longitude": -79.3832,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "raw_payload": {
                "entity_id": entity.id,
            },
        }

        event["risk_score"] = calculate_city_event_risk(event)

        alerts.append(event)

    return alerts


if __name__ == "__main__":
    print("Running TTC GTFS-Realtime ingestor...")

    try:
        alerts = get_ttc_alerts()
        print(f"Collected {len(alerts)} TTC alerts.")

        if not alerts:
            print("No TTC alerts found right now, or the feed returned no active alert entities.")

        for alert in alerts[:10]:
            print("----")
            print("Severity:", alert["severity"])
            print("Title:", alert["title"])
            print("Description:", alert["description"][:300])

    except Exception as error:
        print("TTC ingestion failed:")
        print(error)