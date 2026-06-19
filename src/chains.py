from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import AppConfig


def _format_offers(offers: List[Dict[str, Any]]) -> str:
    if not offers:
        return "Tidak ada flight offer yang ditemukan."

    lines = []

    for index, offer in enumerate(offers, start=1):
        lines.append(
            f"""
Offer {index}
Sumber data: {offer.get("source")}
Maskapai: {offer.get("airline")}
Nomor penerbangan: {offer.get("flight_number")}
Pesawat: {offer.get("airplane")}
Rute: {offer.get("origin")} -> {offer.get("destination")}
Bandara asal: {offer.get("origin_airport")}
Bandara tujuan: {offer.get("destination_airport")}
Berangkat: {offer.get("departure_date")} {offer.get("departure_time")}
Tiba: {offer.get("arrival_date")} {offer.get("arrival_time")}
Durasi: {offer.get("duration")}
Transit: {offer.get("stops")}
Harga: {offer.get("total_amount")} {offer.get("total_currency")}
Budget user: {offer.get("user_budget")} {offer.get("user_budget_currency")}
Masuk budget: {offer.get("within_budget")}
Emisi karbon: {offer.get("carbon_emissions")}
"""
        )

    return "\n".join(lines)


def _fallback_recommendation(inputs: Dict[str, Any]) -> str:
    offers = inputs.get("offers", [])
    budget = inputs.get("budget", 0)
    budget_currency = inputs.get("budget_currency", "")

    if not offers:
        return (
            "Tidak ada penerbangan yang ditemukan. "
            "Coba ganti rute atau tanggal keberangkatan."
        )

    best_offer = offers[0]

    return f"""
Mode fallback tanpa Gemini.

Bandara asal:
{inputs.get("origin_name")} ({inputs.get("origin")})

Bandara tujuan:
{inputs.get("destination_name")} ({inputs.get("destination")})

Rekomendasi penerbangan termurah:
- Maskapai: {best_offer.get("airline")}
- Nomor penerbangan: {best_offer.get("flight_number")}
- Pesawat: {best_offer.get("airplane")}
- Rute: {best_offer.get("origin")} ke {best_offer.get("destination")}
- Berangkat: {best_offer.get("departure_date")} {best_offer.get("departure_time")}
- Tiba: {best_offer.get("arrival_date")} {best_offer.get("arrival_time")}
- Durasi: {best_offer.get("duration")}
- Transit: {best_offer.get("stops")}
- Harga: {best_offer.get("total_amount")} {best_offer.get("total_currency")}

Budget pengguna:
{budget} {budget_currency}

Catatan:
Isi GOOGLE_API_KEY di file .env agar rekomendasi dibuat dengan Gemini API.
"""


def build_recommendation_chain(config: AppConfig):
    if not config.google_api_key:
        return RunnableLambda(_fallback_recommendation)

    llm = ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
Kamu adalah AI Flight Finder dan Travel Planner berbahasa Indonesia.

Tugas kamu:
1. Membaca daftar penerbangan dari SearchAPI Google Flights.
2. Memperhatikan bandara spesifik yang dipilih user.
3. Membandingkan harga, durasi, transit, maskapai, nomor penerbangan, pesawat, dan budget user.
4. Memilih penerbangan terbaik berdasarkan data yang tersedia.
5. Jangan mengarang maskapai, nomor penerbangan, harga, atau jadwal.
6. Jika semua penerbangan melebihi budget, jelaskan dengan sopan.
7. Jika ada data pesawat yang kosong, tulis bahwa data pesawat tidak tersedia.
"""
            ),
            (
                "human",
                """
Data pencarian user:

Asal:
- Kota: {origin_city}
- Bandara spesifik: {origin_name}
- Kode IATA: {origin}

Tujuan:
- Kota: {destination_city}
- Bandara spesifik: {destination_name}
- Kode IATA: {destination}

Detail perjalanan:
- Tipe perjalanan: {flight_type}
- Tanggal berangkat: {departure_date}
- Tanggal pulang: {return_date}
- Jumlah penumpang dewasa: {adults}
- Cabin class: {cabin_class}
- Budget user: {budget} {budget_currency}

Daftar flight offer:
{offers_text}

Buat rekomendasi akhir dalam format:
1. Ringkasan kebutuhan user
2. Bandara asal dan tujuan yang dipilih
3. Rekomendasi penerbangan terbaik
4. Detail maskapai, nomor penerbangan, dan pesawat
5. Alasan pemilihan
6. Analisis budget
7. Catatan transit dan durasi
8. Tips perjalanan singkat
"""
            ),
        ]
    )

    return prompt | llm | StrOutputParser()


def generate_recommendation(
    config: AppConfig,
    state: Dict[str, Any],
) -> str:
    chain = build_recommendation_chain(config)

    offers = state.get("selected_offers", [])

    inputs = {
        "origin": state.get("origin"),
        "origin_name": state.get("origin_name"),
        "origin_city": state.get("origin_city"),

        "destination": state.get("destination"),
        "destination_name": state.get("destination_name"),
        "destination_city": state.get("destination_city"),

        "flight_type": state.get("flight_type"),
        "departure_date": state.get("departure_date"),
        "return_date": state.get("return_date", "-"),

        "adults": state.get("adults"),
        "cabin_class": state.get("cabin_class"),

        "budget": state.get("budget"),
        "budget_currency": state.get("budget_currency"),

        "offers": offers,
        "offers_text": _format_offers(offers),
    }

    return chain.invoke(inputs)
