import random

from app.services.risk_engine import calculate_risk_score

TORONTO_LOCATIONS = [
    {
        "name": "Downtown Core",
        "latitude": 43.6532,
        "longitude": -79.3832,
    },
    {
        "name": "Union Station",
        "latitude": 43.6453,
        "longitude": -79.3806,
    },
    {
        "name": "Yonge-Dundas Square",
        "latitude": 43.6561,
        "longitude": -79.3802,
    },
    {
        "name": "Scarborough Town Centre",
        "latitude": 43.7764,
        "longitude": -79.2571,
    },
    {
        "name": "Toronto Waterfront",
        "latitude": 43.6408,
        "longitude": -79.3767,
    },
]

EVENT_TEMPLATES = [
    {
        "title": "Unexpected congestion detected",
        "category": "traffic",
        "description": "Traffic volume is higher than expected for this hour.",
        "source": "simulated-traffic-engine",
    },
    {
        "title": "Transit delay risk detected",
        "category": "transit",
        "description": "Potential transit delay detected near a high-traffic station.",
        "source": "simulated-transit-engine",
    },
    {
        "title": "Weather disruption risk",
        "category": "weather",
        "description": "Weather conditions may impact nearby mobility and response time.",
        "source": "simulated-weather-engine",
    },
    {
        "title": "Crowd density increase",
        "category": "crowd",
        "description": "Crowd activity is rising above the expected baseline.",
        "source": "simulated-crowd-engine",
    },
    {
        "title": "Emergency activity detected",
        "category": "emergency",
        "description": "Emergency response activity detected in the area.",
        "source": "simulated-emergency-engine",
    },
]

SEVERITIES = ["medium", "high", "critical"]


def generate_city_event():
    location = random.choice(TORONTO_LOCATIONS)
    template = random.choice(EVENT_TEMPLATES)
    severity = random.choice(SEVERITIES)

    risk_score = calculate_risk_score(
        template["category"],
        severity
    )

    return {
        "title": f"{template['title']} near {location['name']}",
        "category": template["category"],
        "severity": severity,
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "description": template["description"],
        "source": template["source"],
        "risk_score": risk_score,
    }