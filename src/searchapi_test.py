import requests
from config import AppConfig


def main():
    config = AppConfig()

    if not config.searchapi_key:
        raise ValueError("SEARCHAPI_KEY belum diisi di file .env")

    url = "https://www.searchapi.io/api/v1/search"

    params = {
        "engine": "google_flights",
        "flight_type": "one_way",
        "departure_id": "LHR",
        "arrival_id": "JFK",
        "outbound_date": "2026-07-17",
        "travel_class": "economy",
        "adults": 1,
        "currency": "USD",
        "sort_by": "price",
        "api_key": config.searchapi_key,
    }

    response = requests.get(url, params=params, timeout=60)

    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    data = response.json()

    print("\n=== SEARCHAPI BERHASIL ===")

    best_flights = data.get("best_flights", [])
    other_flights = data.get("other_flights", [])
    flights = best_flights + other_flights

    print(f"Jumlah hasil: {len(flights)}")

    for index, item in enumerate(flights[:5], start=1):
        price = item.get("price", "-")
        flight_segments = item.get("flights", [])

        if not flight_segments:
            continue

        first = flight_segments[0]
        last = flight_segments[-1]

        airline = first.get("airline", "-")
        flight_number = first.get("flight_number", "-")
        airplane = first.get("airplane", "-")

        dep = first.get("departure_airport", {})
        arr = last.get("arrival_airport", {})

        print(f"\nOffer {index}")
        print(f"Maskapai      : {airline}")
        print(f"No Penerbangan: {flight_number}")
        print(f"Pesawat       : {airplane}")
        print(f"Rute          : {dep.get('id')} -> {arr.get('id')}")
        print(f"Berangkat     : {dep.get('date')} {dep.get('time')}")
        print(f"Tiba          : {arr.get('date')} {arr.get('time')}")
        print(f"Harga         : {price} USD")


if __name__ == "__main__":
    main()
