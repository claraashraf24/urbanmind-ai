from sqlalchemy import func
from app.database import SessionLocal
from app.models.city_alert import CityAlert


db = SessionLocal()

try:
    results = (
        db.query(CityAlert.source, func.count(CityAlert.id))
        .group_by(CityAlert.source)
        .all()
    )

    print("Alert counts by source:")
    for source, count in results:
        print(source, count)

finally:
    db.close()