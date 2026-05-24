import requests
from datetime import datetime, timezone
from app.services.risk_engine import calculate_city_event_risk


TORONTO_LAT = 43.6532
TORONTO_LON = -79.3832


def get_weather_risk_alerts():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={TORONTO_LAT}"
        f"&longitude={TORONTO_LON}"
        "&hourly=temperature_2m,precipitation,rain,snowfall,wind_speed_10m,wind_gusts_10m,visibility,weather_code"
        "&forecast_days=1"
    )

    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    alerts = []

    for i, time_value in enumerate(times):
        rain = hourly.get("rain", [0] * len(times))[i] or 0
        snowfall = hourly.get("snowfall", [0] * len(times))[i] or 0
        wind_speed = hourly.get("wind_speed_10m", [0] * len(times))[i] or 0
        wind_gusts = hourly.get("wind_gusts_10m", [0] * len(times))[i] or 0
        visibility = hourly.get("visibility", [10000] * len(times))[i] or 10000

        severity = None
        title = None

        if rain >= 5 or wind_gusts >= 45 or visibility < 2000:
            severity = "high"
            title = "Weather conditions may increase city disruption risk"
        elif rain >= 2 or snowfall > 0 or wind_speed >= 30:
            severity = "medium"
            title = "Moderate weather risk detected"

        if severity:
            event = {
            "source": "open-meteo",
            "category": "weather",
            "severity": severity,
            "title": title,
            "description": (
                f"Forecast at {time_value}: rain={rain}mm, "
                f"snowfall={snowfall}cm, wind={wind_speed}km/h, "
                f"gusts={wind_gusts}km/h, visibility={visibility}m."
            ),
            "latitude": TORONTO_LAT,
            "longitude": TORONTO_LON,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "raw_payload": {
                "time": time_value,
                "rain": rain,
                "snowfall": snowfall,
                "wind_speed": wind_speed,
                "wind_gusts": wind_gusts,
                "visibility": visibility,
            },
        }

        event["risk_score"] = calculate_city_event_risk(event)

        alerts.append(event)

    return alerts


if __name__ == "__main__":
    print("Running Open-Meteo weather ingestor...")

    try:
        alerts = get_weather_risk_alerts()
        print(f"Collected {len(alerts)} weather alerts.")

        if not alerts:
            print("No risky weather alerts right now. This means the API worked, but current forecast conditions are normal.")

        for alert in alerts[:5]:
            print("----")
            print("Source:", alert["source"])
            print("Category:", alert["category"])
            print("Severity:", alert["severity"])
            print("Title:", alert["title"])
            print("Description:", alert["description"])

    except Exception as error:
        print("Weather ingestion failed:")
        print(error)