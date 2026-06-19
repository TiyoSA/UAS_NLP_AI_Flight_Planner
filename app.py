from datetime import date, timedelta

import streamlit as st

from src.airports import (
    CURRENCY_OPTIONS,
    format_airport_option,
    get_airport_by_label,
    get_airports,
    get_city_names,
)
from src.config import AppConfig, enable_langsmith
from src.globe_map import get_airport_coordinate, render_globe
from src.workflow import build_flight_workflow


st.set_page_config(
    page_title="AI Flight Finder & Travel Planner",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ AI Flight Finder & Travel Planner")

st.write(
    "Aplikasi UAS NLP berbasis SearchAPI Google Flights, Gemini API, "
    "LangChain, LangGraph, LangSmith, dan Streamlit."
)

config = AppConfig()
enable_langsmith(config)

if "last_route" not in st.session_state:
    st.session_state.last_route = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


def get_default_index(items, value):
    if value in items:
        return items.index(value)
    return 0


def airport_selector(title, default_city):
    city_names = get_city_names()
    default_index = get_default_index(city_names, default_city)

    city = st.selectbox(
        f"Kota {title}",
        options=city_names,
        index=default_index,
    )

    airports = get_airports(city)
    airport_labels = [format_airport_option(airport) for airport in airports]

    selected_label = st.selectbox(
        f"Bandara {title} spesifik",
        options=airport_labels,
    )

    selected_airport = get_airport_by_label(city, selected_label)

    st.caption(selected_airport.get("note", ""))

    return {
        "city": city,
        "code": selected_airport.get("code", ""),
        "name": selected_airport.get("name", ""),
        "note": selected_airport.get("note", ""),
    }


with st.sidebar:
    st.header("Status API")

    if config.searchapi_key:
        st.success("SearchAPI key terisi")
    else:
        st.error("SearchAPI key belum diisi")

    if config.google_api_key:
        st.success("Gemini API key terisi")
    else:
        st.warning("Gemini API key belum diisi, fallback aktif")

    if config.langsmith_api_key:
        st.success("LangSmith API key terisi")
    else:
        st.warning("LangSmith API key belum diisi")

    st.divider()

    st.subheader("Catatan")
    st.write(
        "Globe map memakai koordinat bandara dari daftar internal aplikasi. "
        "Kalau memakai kode bandara manual yang belum ada di daftar koordinat, "
        "rute mungkin tidak tampil di globe."
    )

st.subheader("Form Pencarian Penerbangan")

use_manual_airport = st.checkbox(
    "Masukkan kode bandara manual",
    value=False,
    help="Aktifkan jika bandara yang diinginkan belum ada di daftar."
)

if use_manual_airport:
    col1, col2 = st.columns(2)

    with col1:
        origin_city = st.text_input("Kota asal", value="Jakarta")
        origin = st.text_input("Kode IATA bandara asal", value="CGK")
        origin_name = st.text_input(
            "Nama bandara asal",
            value="Bandara Internasional Soekarno-Hatta"
        )

    with col2:
        destination_city = st.text_input("Kota tujuan", value="Bali / Denpasar")
        destination = st.text_input("Kode IATA bandara tujuan", value="DPS")
        destination_name = st.text_input(
            "Nama bandara tujuan",
            value="Bandara Internasional I Gusti Ngurah Rai"
        )

else:
    col1, col2 = st.columns(2)

    with col1:
        origin_airport = airport_selector(
            title="asal",
            default_city="Jakarta",
        )

    with col2:
        destination_airport = airport_selector(
            title="tujuan",
            default_city="Bali / Denpasar",
        )

    origin_city = origin_airport["city"]
    origin = origin_airport["code"]
    origin_name = origin_airport["name"]

    destination_city = destination_airport["city"]
    destination = destination_airport["code"]
    destination_name = destination_airport["name"]

st.divider()

col_trip1, col_trip2 = st.columns(2)

with col_trip1:
    flight_type_label = st.selectbox(
        "Tipe perjalanan",
        options=["Sekali jalan", "Pulang pergi"],
        index=0,
    )

with col_trip2:
    flight_type = "one_way" if flight_type_label == "Sekali jalan" else "round_trip"
    st.write("Kode tipe perjalanan:")
    st.code(flight_type)

col3, col4 = st.columns(2)

with col3:
    departure_date = st.date_input(
        "Tanggal berangkat",
        value=date.today() + timedelta(days=30),
        min_value=date.today() + timedelta(days=1),
    )

with col4:
    if flight_type == "round_trip":
        return_date = st.date_input(
            "Tanggal pulang",
            value=date.today() + timedelta(days=37),
            min_value=departure_date + timedelta(days=1),
        )
    else:
        return_date = None
        st.info("Tanggal pulang tidak diperlukan untuk sekali jalan.")

col5, col6, col7 = st.columns(3)

with col5:
    travel_class_label = st.selectbox(
        "Cabin class",
        options=["Economy", "Premium Economy", "Business", "First Class"],
        index=0,
    )

travel_class_map = {
    "Economy": "economy",
    "Premium Economy": "premium_economy",
    "Business": "business",
    "First Class": "first_class",
}

cabin_class = travel_class_map[travel_class_label]

with col6:
    budget_currency = st.selectbox(
        "Mata uang budget",
        options=list(CURRENCY_OPTIONS.keys()),
        index=list(CURRENCY_OPTIONS.keys()).index("IDR"),
    )

with col7:
    budget = st.number_input(
        f"Budget ({budget_currency})",
        min_value=0.0,
        value=2000000.0 if budget_currency == "IDR" else 1000.0,
        step=50000.0 if budget_currency == "IDR" else 50.0,
    )

adults = st.number_input(
    "Jumlah penumpang dewasa",
    min_value=1,
    max_value=9,
    value=1,
    step=1,
)

st.info(
    "Untuk test awal, coba rute populer seperti LHR → JFK atau CGK → DPS. "
    "Jika suatu rute kosong, coba tanggal lain."
)

st.subheader("Ringkasan Pilihan Bandara")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.write("Asal")
    st.write(f"**{origin_city}**")
    st.write(f"{origin_name} `({origin})`")

with summary_col2:
    st.write("Tujuan")
    st.write(f"**{destination_city}**")
    st.write(f"{destination_name} `({destination})`")

origin_coordinate = get_airport_coordinate(origin)
destination_coordinate = get_airport_coordinate(destination)

if not origin_coordinate:
    st.warning(
        f"Koordinat bandara asal {origin} belum tersedia di globe map."
    )

if not destination_coordinate:
    st.warning(
        f"Koordinat bandara tujuan {destination} belum tersedia di globe map."
    )

button_clicked = st.button("Cari dan Buat Rekomendasi", type="primary")

if button_clicked:
    if not origin.strip() or not destination.strip():
        st.error("Bandara asal dan tujuan wajib diisi.")
        st.stop()

    if not config.searchapi_key:
        st.error("SEARCHAPI_KEY belum diisi di file .env.")
        st.stop()

    state = {
        "origin": origin.upper().strip(),
        "origin_name": origin_name,
        "origin_city": origin_city,

        "destination": destination.upper().strip(),
        "destination_name": destination_name,
        "destination_city": destination_city,

        "flight_type": flight_type,
        "departure_date": departure_date.strftime("%Y-%m-%d"),
        "return_date": return_date.strftime("%Y-%m-%d") if return_date else "",

        "adults": int(adults),
        "cabin_class": cabin_class,

        "budget": float(budget),
        "budget_currency": budget_currency,
    }

    with st.spinner("Mencari penerbangan nyata dari Google Flights dan membuat rekomendasi..."):
        workflow = build_flight_workflow(config)
        result = workflow.invoke(state)

    st.session_state.last_route = {
        "origin": origin.upper().strip(),
        "origin_name": origin_name,
        "origin_city": origin_city,
        "destination": destination.upper().strip(),
        "destination_name": destination_name,
        "destination_city": destination_city,
    }

    st.session_state.last_result = result

st.divider()

render_globe(st.session_state.last_route)

if st.session_state.last_result:
    result = st.session_state.last_result

    st.subheader("Rekomendasi AI")
    st.write(result.get("answer", "Tidak ada jawaban."))

    selected_offers = result.get("selected_offers", [])

    if selected_offers:
        st.subheader("Flight Offers dari SearchAPI Google Flights")
        st.dataframe(selected_offers, use_container_width=True)

    with st.expander("Lihat State LangGraph"):
        st.json(result)
