from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.city_alert import CityAlert


def expire_stale_alerts(hours: int = 24):
    db = SessionLocal()

    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        stale_alerts = (
            db.query(CityAlert)
            .filter(CityAlert.status == "active")
            .filter(CityAlert.created_at < cutoff)
            .filter(CityAlert.source.in_(["open-meteo", "ttc-gtfs-realtime"]))
            .all()
        )

        for alert in stale_alerts:
            alert.status = "expired"
            alert.resolved_at = datetime.now(timezone.utc)

        db.commit()
        return len(stale_alerts)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    count = expire_stale_alerts(hours=24)
    print(f"Expired {count} stale weather/TTC alerts.")