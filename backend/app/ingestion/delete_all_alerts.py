from app.database import SessionLocal
from app.models.city_alert import CityAlert


def delete_all_alerts():
    db = SessionLocal()

    try:
        deleted_count = db.query(CityAlert).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    count = delete_all_alerts()
    print(f"Deleted {count} alerts.")