import requests


BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
PACKAGE_ID = "ttc-gtfs-realtime-gtfs-rt"


def main():
    url = BASE_URL + "/api/3/action/package_show"
    params = {"id": PACKAGE_ID}

    package = requests.get(url, params=params, timeout=30).json()

    print("Package title:", package["result"]["title"])
    print()

    for idx, resource in enumerate(package["result"]["resources"], start=1):
        print(f"Resource {idx}")
        print("Name:", resource.get("name"))
        print("Format:", resource.get("format"))
        print("Datastore active:", resource.get("datastore_active"))
        print("URL:", resource.get("url"))
        print("ID:", resource.get("id"))
        print("-" * 80)


if __name__ == "__main__":
    main()