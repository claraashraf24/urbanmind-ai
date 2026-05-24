from typing import Any


SEVERITY_BASE_SCORE = {
    "low": 35,
    "medium": 55,
    "high": 75,
    "critical": 90,
}


ROAD_CLASS_BOOST = {
    "Expressway": 12,
    "Major Arterial Road": 10,
    "Minor Arterial Road": 7,
    "Collector Road": 5,
    "Local Road": 2,
    "Unknown": 0,
}


CURRENT_IMPACT_BOOST = {
    "high": 10,
    "medium": 6,
    "low": 2,
}


def clamp_score(score: float) -> int:
    return max(0, min(100, round(score)))


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def calculate_weather_risk(event: dict) -> int:
    raw = event.get("raw_payload", {})

    severity = event.get("severity", "medium")
    score = SEVERITY_BASE_SCORE.get(severity, 55)

    rain = float(raw.get("rain", 0) or 0)
    snowfall = float(raw.get("snowfall", 0) or 0)
    wind_speed = float(raw.get("wind_speed", 0) or 0)
    wind_gusts = float(raw.get("wind_gusts", 0) or 0)
    visibility = float(raw.get("visibility", 10000) or 10000)

    if rain >= 5:
        score += 8
    elif rain >= 2:
        score += 4

    if snowfall > 0:
        score += 8

    if wind_gusts >= 60:
        score += 10
    elif wind_gusts >= 45:
        score += 6

    if wind_speed >= 35:
        score += 5

    if visibility < 1000:
        score += 10
    elif visibility < 3000:
        score += 5

    return clamp_score(score)


def calculate_ttc_risk(event: dict) -> int:
    severity = event.get("severity", "medium")
    score = SEVERITY_BASE_SCORE.get(severity, 55)

    text = normalize_text(event.get("title", "")) + " " + normalize_text(
        event.get("description", "")
    )

    if "no subway service" in text:
        score += 15

    if "shuttle buses" in text:
        score += 10

    if "collision" in text:
        score += 10

    if "downed electrical wire" in text:
        score += 10

    if "detour" in text:
        score += 6

    if "delay" in text:
        score += 5

    if "elevator" in text or "escalator" in text:
        score -= 8

    return clamp_score(score)


def calculate_road_risk(event: dict) -> int:
    severity = event.get("severity", "medium")
    score = SEVERITY_BASE_SCORE.get(severity, 55)

    raw = event.get("raw_payload", {})

    road_class = raw.get("RoadClass", "Unknown")
    curr_impact = normalize_text(raw.get("CurrImpact", ""))
    max_impact = normalize_text(raw.get("MaxImpact", ""))
    planned = normalize_text(raw.get("Planned", ""))

    source = normalize_text(raw.get("Source", ""))
    description = normalize_text(raw.get("Description", ""))
    title = normalize_text(event.get("title", ""))

    score += ROAD_CLASS_BOOST.get(road_class, 0)

    if curr_impact in CURRENT_IMPACT_BOOST:
        score += CURRENT_IMPACT_BOOST[curr_impact]

    if max_impact in CURRENT_IMPACT_BOOST:
        score += CURRENT_IMPACT_BOOST[max_impact]

    if planned in ["0", "false", "no"]:
        score += 8

    if "full closure" in description or "full closure" in title:
        score += 12

    if "closed" in description or "closure" in description:
        score += 8

    if "collision" in description or "collision" in source:
        score += 10

    if "emergency" in description or "emergency" in source:
        score += 10

    if "construction" in description or "construction" in source:
        score += 3

    return clamp_score(score)


def calculate_city_event_risk(event: dict) -> int:
    source = event.get("source", "")
    category = event.get("category", "")

    if source == "open-meteo" or category == "weather":
        return calculate_weather_risk(event)

    if source == "ttc-gtfs-realtime" or category == "transit":
        return calculate_ttc_risk(event)

    if source == "toronto-road-restrictions" or category == "traffic":
        return calculate_road_risk(event)

    severity = event.get("severity", "medium")
    return clamp_score(SEVERITY_BASE_SCORE.get(severity, 55))


def explain_risk(event: dict) -> list[str]:
    reasons = []

    source = event.get("source", "")
    severity = event.get("severity", "medium")
    raw = event.get("raw_payload", {})
    text = normalize_text(event.get("title", "")) + " " + normalize_text(
        event.get("description", "")
    )

    reasons.append(f"Base severity is {severity}.")

    if source == "open-meteo":
        rain = float(raw.get("rain", 0) or 0)
        wind_gusts = float(raw.get("wind_gusts", 0) or 0)
        visibility = float(raw.get("visibility", 10000) or 10000)

        if rain >= 2:
            reasons.append(f"Rain level is elevated at {rain}mm.")

        if wind_gusts >= 45:
            reasons.append(f"Wind gusts are high at {wind_gusts}km/h.")

        if visibility < 3000:
            reasons.append(f"Visibility is reduced at {visibility}m.")

    elif source == "ttc-gtfs-realtime":
        if "no subway service" in text:
            reasons.append("TTC alert indicates no subway service.")

        if "shuttle buses" in text:
            reasons.append("Shuttle buses are required, increasing disruption impact.")

        if "collision" in text:
            reasons.append("Transit disruption is related to a collision.")

        if "elevator" in text or "escalator" in text:
            reasons.append("Elevator/escalator outage affects accessibility but has lower city-wide impact.")

    elif source == "toronto-road-restrictions":
        road_class = raw.get("RoadClass")

        if road_class:
            reasons.append(f"Road class is {road_class}.")

        curr_impact = raw.get("CurrImpact")
        max_impact = raw.get("MaxImpact")

        if curr_impact:
            reasons.append(f"Current impact is {curr_impact}.")

        if max_impact:
            reasons.append(f"Maximum impact is {max_impact}.")

        if raw.get("Planned") in ["0", 0, False]:
            reasons.append("Restriction appears unplanned.")

    return reasons