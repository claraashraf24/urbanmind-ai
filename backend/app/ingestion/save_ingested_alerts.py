from app.database import SessionLocal
from app.models.city_alert import CityAlert
from app.ingestion.run_ingestion import run_all_ingestors


def serialize_alert(alert: CityAlert) -> dict:
    return {
        "id": alert.id,
        "title": alert.title,
        "category": alert.category,
        "severity": alert.severity,
        "latitude": alert.latitude,
        "longitude": alert.longitude,
        "description": alert.description,
        "source": alert.source,
        "risk_score": alert.risk_score,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "raw_payload": alert.raw_payload,
    }


def save_events_to_database(events):
    db = SessionLocal()
    saved_alerts = []
    skipped_count = 0

    try:
        for event in events:
            existing = (
                db.query(CityAlert)
                .filter(CityAlert.title == event["title"])
                .filter(CityAlert.source == event["source"])
                .filter(CityAlert.latitude == event["latitude"])
                .filter(CityAlert.longitude == event["longitude"])
                .first()
            )

            if existing:
                skipped_count += 1
                continue

            alert = CityAlert(
                title=event["title"],
                category=event["category"],
                severity=event["severity"],
                latitude=event["latitude"],
                longitude=event["longitude"],
                description=event.get("description"),
                source=event["source"],
                risk_score=event.get("risk_score", 0),
                raw_payload=event.get("raw_payload"),
            )

            db.add(alert)
            db.flush()
            db.refresh(alert)

            saved_alerts.append(serialize_alert(alert))

        db.commit()

        return saved_alerts, skipped_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def ingest_and_save_events():
    events = run_all_ingestors()
    saved_alerts, skipped_count = save_events_to_database(events)

    return {
        "collected": len(events),
        "saved": len(saved_alerts),
        "skipped": skipped_count,
        "saved_alerts": saved_alerts,
    }


if __name__ == "__main__":
    print("Collecting real city events...")

    result = ingest_and_save_events()

    print(f"Collected {result['collected']} events.")
    print(f"Saved {result['saved']} new alerts.")
    print(f"Skipped {result['skipped']} duplicate alerts.")

    if result["saved_alerts"]:
        print("\nNew alerts:")
        for alert in result["saved_alerts"][:10]:
            print("----")
            print(alert["source"], "|", alert["category"], "|", alert["severity"])
            print(alert["title"])