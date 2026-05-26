from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.city_alert import CityAlert


def cleanup_old_alerts(days: int = 7):
    db = SessionLocal()

    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        deleted_count = (
            db.query(CityAlert)
            .filter(CityAlert.created_at < cutoff)
            .delete(synchronize_session=False)
        )

        db.commit()
        return deleted_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    count = cleanup_old_alerts(days=7)
    print(f"Deleted {count} alerts older than 7 days.")