from app.database import SessionLocal
from app.models.city_alert import CityAlert
from app.services.risk_engine import calculate_risk_score

db = SessionLocal()



alerts = [
    {
        "title": "Unexpected congestion detected",
        "category": "traffic",
        "severity": "high",
        "latitude": 43.6532,
        "longitude": -79.3832,
        "description": "Heavy traffic detected near Downtown Core.",
        "source": "anomaly-engine"
    },
    {
        "title": "TTC Line Delay",
        "category": "transit",
        "severity": "medium",
        "latitude": 43.6426,
        "longitude": -79.3871,
        "description": "Minor TTC delay reported near Union Station.",
        "source": "ttc-api"
    },
    {
        "title": "Severe rainfall warning",
        "category": "weather",
        "severity": "high",
        "latitude": 43.7001,
        "longitude": -79.4163,
        "description": "Heavy rainfall expected in Midtown Toronto.",
        "source": "weather-api"
    },
    {
        "title": "Crowd density spike detected",
        "category": "crowd",
        "severity": "critical",
        "latitude": 43.6510,
        "longitude": -79.3470,
        "description": "Abnormal crowd activity near event zone.",
        "source": "crowd-engine"
    },
    {
        "title": "Emergency response activity",
        "category": "emergency",
        "severity": "critical",
        "latitude": 43.6629,
        "longitude": -79.3957,
        "description": "Emergency vehicles dispatched.",
        "source": "city-emergency"
    }
]



for alert in alerts:
    alert["risk_score"] = calculate_risk_score(
        alert["category"],
        alert["severity"]
    )

    existing = db.query(CityAlert).filter(
        CityAlert.title == alert["title"]
    ).first()

    if not existing:
        db.add(CityAlert(**alert))

db.commit()

print("Toronto alerts seeded successfully.")