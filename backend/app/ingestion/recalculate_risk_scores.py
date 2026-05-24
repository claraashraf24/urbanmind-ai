from app.database import SessionLocal
from app.models.city_alert import CityAlert
from app.services.risk_engine import calculate_city_event_risk


def recalculate_all_scores():
    db = SessionLocal()
    updated_count = 0

    try:
        alerts = db.query(CityAlert).all()

        for alert in alerts:
            event = {
                "source": alert.source,
                "category": alert.category,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "raw_payload": {},
            }

            new_score = calculate_city_event_risk(event)

            if alert.risk_score != new_score:
                alert.risk_score = new_score
                updated_count += 1

        db.commit()
        return updated_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    count = recalculate_all_scores()
    print(f"Updated risk scores for {count} alerts.")