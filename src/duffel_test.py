import requests
from config import AppConfig


def main():
    config = AppConfig()

    if not config.duffel_access_token:
        raise ValueError(
            "DUFFEL_ACCESS_TOKEN belum diisi di file .env"
        )

    url = "https://api.duffel.com/air/airports"

    headers = {
        "Authorization": f"Bearer {config.duffel_access_token}",
        "Duffel-Version": "v2",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
    }

    params = {
        "limit": 10,
        "iata_country_code": "ID",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("\\n=== TOKEN DUFFEL BERHASIL ===")
        print("Daftar airport Indonesia dari Duffel:\\n")

        airports = data.get("data", [])

        if not airports:
            print("Data airport kosong.")
            return

        for airport in airports:
            print(
                f"- {airport.get('iata_code')} | "
                f"{airport.get('name')} | "
                f"{airport.get('city_name')}"
            )

    else:
        print("\\n=== ERROR DARI DUFFEL ===")
        print(response.text)


if __name__ == "__main__":
    main()
