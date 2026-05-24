import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_toronto_hospitals():
    query = """
    [out:json][timeout:25];
    area["name"="Toronto"]["boundary"="administrative"]->.searchArea;
    (
      node["amenity"="hospital"](area.searchArea);
      way["amenity"="hospital"](area.searchArea);
      relation["amenity"="hospital"](area.searchArea);
    );
    out center;
    """

    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
    response.raise_for_status()
    data = response.json()

    places = []

    for element in data["elements"]:
        tags = element.get("tags", {})
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")

        if lat and lon:
            places.append({
                "name": tags.get("name", "Hospital"),
                "place_type": "hospital",
                "latitude": lat,
                "longitude": lon,
                "raw_payload": element,
            })

    return places