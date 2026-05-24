from app.ingestion.weather_ingestor import get_weather_risk_alerts
from app.ingestion.ttc_ingestor import get_ttc_alerts
from app.ingestion.road_ingestor import get_road_restriction_alerts


def run_all_ingestors():
    events = []

    try:
        weather_alerts = get_weather_risk_alerts()
        print(f"Weather alerts: {len(weather_alerts)}")
        events.extend(weather_alerts)
    except Exception as error:
        print("Weather ingestion failed:", error)

    try:
        ttc_alerts = get_ttc_alerts()
        print(f"TTC alerts: {len(ttc_alerts)}")
        events.extend(ttc_alerts)
    except Exception as error:
        print("TTC ingestion failed:", error)

    try:
        road_alerts = get_road_restriction_alerts()
        print(f"Road restriction alerts: {len(road_alerts)}")
        events.extend(road_alerts)
    except Exception as error:
        print("Road restriction ingestion failed:", error)

    return events


if __name__ == "__main__":
    print("Running all UrbanMind AI ingestors...")
    events = run_all_ingestors()

    print()
    print(f"Total collected events: {len(events)}")

    for event in events[:20]:
        print("----")
        print("Source:", event["source"])
        print("Category:", event["category"])
        print("Severity:", event["severity"])
        print("Title:", event["title"])
        print("Lat/Lon:", event["latitude"], event["longitude"])