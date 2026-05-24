import csv
import io
import requests
from datetime import datetime, timezone
from app.services.risk_engine import calculate_city_event_risk


ROAD_RESTRICTIONS_URL = "https://secure.toronto.ca/opendata/cart/road_restrictions/v3?format=csv"


def classify_road_severity(title, description):
    text = f"{title} {description}".lower()

    if any(word in text for word in ["emergency", "collision", "major", "full closure", "closed fully"]):
        return "critical"

    if any(word in text for word in ["closed", "closure", "restricted", "construction", "lane"]):
        return "high"

    return "medium"


def safe_float(value, fallback):
    try:
        if value is None or value == "":
            return fallback
        return float(value)
    except Exception:
        return fallback


def first_available(record, keys, fallback=None):
    for key in keys:
        if key in record and record[key] not in [None, ""]:
            return record[key]
    return fallback


def normalize_record(record):
    road = first_available(record, ["Road"], "")
    name = first_available(record, ["Name"], "")
    district = first_available(record, ["District"], "")
    road_class = first_available(record, ["RoadClass"], "")
    planned = first_available(record, ["Planned"], "")
    source = first_available(record, ["Source"], "")
    work_event = first_available(record, ["WorkEvent"], "")
    restriction = first_available(record, ["WorkPeriod"], "")
    start_time = first_available(record, ["StartTime"], "")
    end_time = first_available(record, ["EndTime"], "")

    title = name or road or "Road restriction detected"

    description = (
        f"Road: {road}. "
        f"District: {district}. "
        f"Road class: {road_class}. "
        f"Work event: {work_event}. "
        f"Restriction period: {restriction}. "
        f"Planned: {planned}. "
        f"Source: {source}. "
        f"Start: {start_time}. "
        f"End: {end_time}."
    )

    latitude = first_available(record, ["Latitude"], 43.6532)
    longitude = first_available(record, ["Longitude"], -79.3832)

    severity = classify_road_severity(title, description)

    event = {
        "source": "toronto-road-restrictions",
        "category": "traffic",
        "severity": severity,
        "title": str(title),
        "description": description,
        "latitude": safe_float(latitude, 43.6532),
        "longitude": safe_float(longitude, -79.3832),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_payload": record,
    }

    event["risk_score"] = calculate_city_event_risk(event)

    return event

def get_road_restriction_alerts():
    response = requests.get(ROAD_RESTRICTIONS_URL, timeout=30)
    response.raise_for_status()

    # print("Response status:", response.status_code)
    # print("Content type:", response.headers.get("content-type"))
    # print("First 200 chars:", response.text[:200])

    csv_text = response.text

    csv_lines = csv_text.splitlines()

    # Toronto road restrictions CSV starts with a title line:
    # "Current road restrictions"
    # The real header starts on the second line.
    if csv_lines and csv_lines[0].strip().lower() == "current road restrictions":
        csv_text = "\n".join(csv_lines[1:])

    reader = csv.DictReader(io.StringIO(csv_text))
    records = list(reader)

    # print("CSV columns:", reader.fieldnames)
    # print("Total raw road records:", len(records))

    alerts = []

    for record in records:
        alerts.append(normalize_record(record))

    return alerts


if __name__ == "__main__":
    print("Running Toronto Road Restrictions ingestor...")

    try:
        alerts = get_road_restriction_alerts()
        print(f"Collected {len(alerts)} road restriction alerts.")

        for alert in alerts[:10]:
            print("----")
            print("Severity:", alert["severity"])
            print("Title:", alert["title"])
            print("Lat/Lon:", alert["latitude"], alert["longitude"])
            print("Description:", alert["description"][:300])

    except Exception as error:
        print("Road restriction ingestion failed:")
        print(error)