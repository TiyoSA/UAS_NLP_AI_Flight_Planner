from typing import Any, Dict, List
import requests


class DuffelAPIError(Exception):
    """Error khusus untuk Duffel API."""


class DuffelClient:
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("DUFFEL_ACCESS_TOKEN belum diisi di file .env")

        self.access_token = access_token
        self.base_url = "https://api.duffel.com"

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Duffel-Version": "v2",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
        cabin_class: str = "economy",
        max_offers: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Mencari flight offer dari Duffel API.

        Parameter:
        - origin: kode IATA asal, contoh CGK, DPS, LHR
        - destination: kode IATA tujuan
        - departure_date: tanggal berangkat format YYYY-MM-DD
        - adults: jumlah penumpang dewasa
        - cabin_class: economy, premium_economy, business, first
        """

        url = f"{self.base_url}/air/offer_requests"

        passengers = [{"type": "adult"} for _ in range(adults)]

        payload = {
            "data": {
                "slices": [
                    {
                        "origin": origin.upper().strip(),
                        "destination": destination.upper().strip(),
                        "departure_date": departure_date,
                    }
                ],
                "passengers": passengers,
                "cabin_class": cabin_class,
            }
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=60,
        )

        if response.status_code not in [200, 201]:
            raise DuffelAPIError(
                f"Duffel API error {response.status_code}: {response.text}"
            )

        data = response.json()
        offers = data.get("data", {}).get("offers", [])

        simplified_offers = []

        for offer in offers[:max_offers]:
            simplified_offers.append(self._simplify_offer(offer))

        return simplified_offers

    def _simplify_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mengambil bagian penting dari offer agar mudah dibaca oleh Gemini dan Streamlit.
        """

        slices = offer.get("slices", [])
        first_slice = slices[0] if slices else {}

        segments = first_slice.get("segments", [])
        first_segment = segments[0] if segments else {}
        last_segment = segments[-1] if segments else {}

        airline = offer.get("owner", {}).get("name", "Unknown Airline")

        total_amount = offer.get("total_amount", "0")
        total_currency = offer.get("total_currency", "-")

        origin = first_segment.get("origin", {}).get("iata_code", "-")
        destination = last_segment.get("destination", {}).get("iata_code", "-")

        departing_at = first_segment.get("departing_at", "-")
        arriving_at = last_segment.get("arriving_at", "-")

        duration = first_slice.get("duration", "-")
        stops = max(len(segments) - 1, 0)

        return {
            "offer_id": offer.get("id", "-"),
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "departure_time": departing_at,
            "arrival_time": arriving_at,
            "duration": duration,
            "stops": stops,
            "total_amount": total_amount,
            "total_currency": total_currency,
        }
