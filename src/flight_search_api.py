from typing import Any, Dict, List, Optional

import requests


class FlightSearchAPIError(Exception):
    """Error khusus untuk SearchAPI Google Flights."""


def format_minutes(minutes: Optional[int]) -> str:
    if minutes is None:
        return "-"

    try:
        minutes = int(minutes)
    except ValueError:
        return "-"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours and remaining_minutes:
        return f"{hours} jam {remaining_minutes} menit"

    if hours:
        return f"{hours} jam"

    return f"{remaining_minutes} menit"


class GoogleFlightsSearchClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("SEARCHAPI_KEY belum diisi di file .env")

        self.api_key = api_key
        self.base_url = "https://www.searchapi.io/api/v1/search"

    def search_flights(
        self,
        origin: str,
        destination: str,
        outbound_date: str,
        return_date: str = "",
        flight_type: str = "one_way",
        adults: int = 1,
        travel_class: str = "economy",
        currency: str = "USD",
        max_offers: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Mencari flight offer dari SearchAPI Google Flights.

        Parameter:
        - origin: kode IATA asal, contoh CGK, DPS, LHR
        - destination: kode IATA tujuan
        - outbound_date: tanggal berangkat format YYYY-MM-DD
        - return_date: tanggal pulang, wajib jika round_trip
        - flight_type: one_way atau round_trip
        - adults: jumlah penumpang dewasa
        - travel_class: economy, premium_economy, business, first_class
        - currency: IDR, USD, SGD, MYR, EUR, dll
        """

        params = {
            "engine": "google_flights",
            "flight_type": flight_type,
            "departure_id": origin.upper().strip(),
            "arrival_id": destination.upper().strip(),
            "outbound_date": outbound_date,
            "travel_class": travel_class,
            "adults": adults,
            "currency": currency,
            "sort_by": "price",
            "api_key": self.api_key,
        }

        if flight_type == "round_trip":
            if not return_date:
                raise ValueError("return_date wajib diisi untuk round_trip")

            params["return_date"] = return_date

        response = requests.get(
            self.base_url,
            params=params,
            timeout=90,
        )

        if response.status_code != 200:
            raise FlightSearchAPIError(
                f"SearchAPI error {response.status_code}: {response.text}"
            )

        data = response.json()

        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])

        offers = best_flights + other_flights

        simplified_offers = []

        for offer in offers[:max_offers]:
            simplified_offers.append(
                self._simplify_offer(
                    offer=offer,
                    currency=currency,
                )
            )

        return simplified_offers

    def _simplify_offer(
        self,
        offer: Dict[str, Any],
        currency: str,
    ) -> Dict[str, Any]:
        flights = offer.get("flights", [])

        first_flight = flights[0] if flights else {}
        last_flight = flights[-1] if flights else {}

        departure_airport = first_flight.get("departure_airport", {})
        arrival_airport = last_flight.get("arrival_airport", {})

        airlines = []
        flight_numbers = []
        airplanes = []

        for flight in flights:
            airline = flight.get("airline")
            flight_number = flight.get("flight_number")
            airplane = flight.get("airplane")

            if airline and airline not in airlines:
                airlines.append(airline)

            if flight_number and flight_number not in flight_numbers:
                flight_numbers.append(flight_number)

            if airplane and airplane not in airplanes:
                airplanes.append(airplane)

        price = offer.get("price", 0)
        total_duration = offer.get("total_duration")

        layovers = offer.get("layovers", [])
        stops = max(len(flights) - 1, 0)

        carbon_emissions = offer.get("carbon_emissions", {})
        this_flight_emission = carbon_emissions.get("this_flight")

        if this_flight_emission:
            emission_text = f"{round(this_flight_emission / 1000, 1)} kg CO2"
        else:
            emission_text = "-"

        return {
            "source": "SearchAPI Google Flights",
            "airline": ", ".join(airlines) if airlines else "-",
            "flight_number": ", ".join(flight_numbers) if flight_numbers else "-",
            "airplane": ", ".join(airplanes) if airplanes else "-",

            "origin": departure_airport.get("id", "-"),
            "origin_airport": departure_airport.get("name", "-"),
            "destination": arrival_airport.get("id", "-"),
            "destination_airport": arrival_airport.get("name", "-"),

            "departure_date": departure_airport.get("date", "-"),
            "departure_time": departure_airport.get("time", "-"),
            "arrival_date": arrival_airport.get("date", "-"),
            "arrival_time": arrival_airport.get("time", "-"),

            "duration_minutes": total_duration,
            "duration": format_minutes(total_duration),
            "stops": stops,
            "layovers": layovers,

            "total_amount": price,
            "total_currency": currency,

            "carbon_emissions": emission_text,
            "booking_token": offer.get("booking_token", "-"),
            "departure_token": offer.get("departure_token", "-"),
        }
