from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from src.chains import generate_recommendation
from src.config import AppConfig
from src.flight_search_api import GoogleFlightsSearchClient


class FlightState(TypedDict, total=False):
    origin: str
    origin_name: str
    origin_city: str

    destination: str
    destination_name: str
    destination_city: str

    flight_type: str
    departure_date: str
    return_date: str

    adults: int
    cabin_class: str

    budget: float
    budget_currency: str

    raw_offers: List[Dict[str, Any]]
    selected_offers: List[Dict[str, Any]]

    answer: str
    error: str


def build_flight_workflow(config: AppConfig):
    """
    Workflow LangGraph:

    START
      -> search_flights
      -> analyze_offers
      -> generate_final_answer
    END
    """

    @traceable(name="search_flights_with_searchapi_google_flights")
    def search_flights(state: FlightState) -> FlightState:
        try:
            client = GoogleFlightsSearchClient(config.searchapi_key)

            offers = client.search_flights(
                origin=state["origin"],
                destination=state["destination"],
                outbound_date=state["departure_date"],
                return_date=state.get("return_date", ""),
                flight_type=state.get("flight_type", "one_way"),
                adults=state.get("adults", 1),
                travel_class=state.get("cabin_class", "economy"),
                currency=state.get("budget_currency", "USD"),
                max_offers=8,
            )

            return {
                "raw_offers": offers,
                "error": "",
            }

        except Exception as error:
            return {
                "raw_offers": [],
                "selected_offers": [],
                "answer": "",
                "error": str(error),
            }

    @traceable(name="analyze_flight_offers")
    def analyze_offers(state: FlightState) -> FlightState:
        offers = state.get("raw_offers", [])

        if not offers:
            return {
                "selected_offers": [],
            }

        def price_to_float(offer: Dict[str, Any]) -> float:
            try:
                return float(offer.get("total_amount", 0))
            except (ValueError, TypeError):
                return 999999999.0

        sorted_offers = sorted(offers, key=price_to_float)

        user_budget = float(state.get("budget", 0) or 0)

        selected = []

        for offer in sorted_offers[:5]:
            offer_price = price_to_float(offer)

            offer["user_budget"] = user_budget
            offer["user_budget_currency"] = state.get("budget_currency", "USD")
            offer["within_budget"] = user_budget <= 0 or offer_price <= user_budget

            selected.append(offer)

        return {
            "selected_offers": selected,
        }

    @traceable(name="generate_final_recommendation")
    def generate_final_answer(state: FlightState) -> FlightState:
        if state.get("error"):
            return {
                "answer": (
                    "Terjadi error saat mencari penerbangan.\n\n"
                    f"Detail error:\n{state.get('error')}\n\n"
                    "Coba cek SEARCHAPI_KEY, kode bandara, tanggal keberangkatan, "
                    "atau sisa kuota SearchAPI."
                )
            }

        if not state.get("selected_offers"):
            return {
                "answer": (
                    "Tidak ada penerbangan yang ditemukan.\n\n"
                    "Coba gunakan rute, tanggal, atau kelas penerbangan lain."
                )
            }

        answer = generate_recommendation(config, state)

        return {
            "answer": answer,
        }

    graph = StateGraph(FlightState)

    graph.add_node("search_flights", search_flights)
    graph.add_node("analyze_offers", analyze_offers)
    graph.add_node("generate_final_answer", generate_final_answer)

    graph.add_edge(START, "search_flights")
    graph.add_edge("search_flights", "analyze_offers")
    graph.add_edge("analyze_offers", "generate_final_answer")
    graph.add_edge("generate_final_answer", END)

    return graph.compile()
