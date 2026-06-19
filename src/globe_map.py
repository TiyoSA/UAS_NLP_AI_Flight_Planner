import math
from typing import Dict, Optional

import plotly.graph_objects as go
import streamlit as st


AIRPORT_COORDINATES = {
    "CGK": {"lat": -6.1256, "lon": 106.6559, "name": "Bandara Internasional Soekarno-Hatta"},
    "HLP": {"lat": -6.2666, "lon": 106.8911, "name": "Bandara Halim Perdanakusuma"},
    "DPS": {"lat": -8.7482, "lon": 115.1670, "name": "Bandara Internasional I Gusti Ngurah Rai"},
    "PKU": {"lat": 0.4608, "lon": 101.4445, "name": "Bandara Sultan Syarif Kasim II"},
    "BTH": {"lat": 1.1210, "lon": 104.1188, "name": "Bandara Hang Nadim"},
    "KNO": {"lat": 3.6422, "lon": 98.8853, "name": "Bandara Internasional Kualanamu"},
    "SUB": {"lat": -7.3798, "lon": 112.7869, "name": "Bandara Internasional Juanda"},
    "YIA": {"lat": -7.9053, "lon": 110.0573, "name": "Yogyakarta International Airport"},
    "JOG": {"lat": -7.7882, "lon": 110.4318, "name": "Bandara Adisutjipto"},

    "SIN": {"lat": 1.3644, "lon": 103.9915, "name": "Singapore Changi Airport"},
    "XSP": {"lat": 1.4169, "lon": 103.8676, "name": "Seletar Airport"},
    "KUL": {"lat": 2.7456, "lon": 101.7072, "name": "Kuala Lumpur International Airport"},
    "SZB": {"lat": 3.1306, "lon": 101.5493, "name": "Sultan Abdul Aziz Shah Airport"},

    "BKK": {"lat": 13.6900, "lon": 100.7501, "name": "Suvarnabhumi Airport"},
    "DMK": {"lat": 13.9126, "lon": 100.6068, "name": "Don Mueang International Airport"},

    "HND": {"lat": 35.5494, "lon": 139.7798, "name": "Tokyo Haneda Airport"},
    "NRT": {"lat": 35.7720, "lon": 140.3929, "name": "Narita International Airport"},

    "LHR": {"lat": 51.4700, "lon": -0.4543, "name": "London Heathrow Airport"},
    "LGW": {"lat": 51.1537, "lon": -0.1821, "name": "London Gatwick Airport"},
    "STN": {"lat": 51.8850, "lon": 0.2350, "name": "London Stansted Airport"},
    "LCY": {"lat": 51.5053, "lon": 0.0553, "name": "London City Airport"},

    "JFK": {"lat": 40.6413, "lon": -73.7781, "name": "John F. Kennedy International Airport"},
    "EWR": {"lat": 40.6895, "lon": -74.1745, "name": "Newark Liberty International Airport"},
    "LGA": {"lat": 40.7769, "lon": -73.8740, "name": "LaGuardia Airport"},
}


def get_airport_coordinate(iata_code: str) -> Optional[Dict]:
    return AIRPORT_COORDINATES.get(iata_code.upper().strip())


def great_circle_points(lat1, lon1, lat2, lon2, points=80):
    """
    Membuat titik-titik lengkung rute di permukaan bumi.
    Ini membuat garis terlihat seperti jalur penerbangan global.
    """

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta = 2 * math.asin(
        math.sqrt(
            math.sin((lat2_rad - lat1_rad) / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin((lon2_rad - lon1_rad) / 2) ** 2
        )
    )

    if delta == 0:
        return [lat1], [lon1]

    latitudes = []
    longitudes = []

    for i in range(points):
        fraction = i / (points - 1)

        a = math.sin((1 - fraction) * delta) / math.sin(delta)
        b = math.sin(fraction * delta) / math.sin(delta)

        x = (
            a * math.cos(lat1_rad) * math.cos(lon1_rad)
            + b * math.cos(lat2_rad) * math.cos(lon2_rad)
        )
        y = (
            a * math.cos(lat1_rad) * math.sin(lon1_rad)
            + b * math.cos(lat2_rad) * math.sin(lon2_rad)
        )
        z = a * math.sin(lat1_rad) + b * math.sin(lat2_rad)

        lat = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
        lon = math.degrees(math.atan2(y, x))

        latitudes.append(lat)
        longitudes.append(lon)

    return latitudes, longitudes


def build_globe_figure(route: Optional[Dict] = None):
    fig = go.Figure()

    if route:
        origin_code = route.get("origin", "")
        destination_code = route.get("destination", "")

        origin = get_airport_coordinate(origin_code)
        destination = get_airport_coordinate(destination_code)

        if origin and destination:
            route_lats, route_lons = great_circle_points(
                origin["lat"],
                origin["lon"],
                destination["lat"],
                destination["lon"],
            )

            fig.add_trace(
                go.Scattergeo(
                    lon=route_lons,
                    lat=route_lats,
                    mode="lines",
                    name="Jejak rute penerbangan",
                    hoverinfo="text",
                    text=[
                        f"{origin_code} menuju {destination_code}"
                        for _ in route_lats
                    ],
                )
            )

            fig.add_trace(
                go.Scattergeo(
                    lon=[origin["lon"], destination["lon"]],
                    lat=[origin["lat"], destination["lat"]],
                    mode="markers+text",
                    text=[
                        f"{origin_code}",
                        f"{destination_code}",
                    ],
                    textposition="top center",
                    name="Bandara",
                    hovertext=[
                        f"Asal: {origin['name']} ({origin_code})",
                        f"Tujuan: {destination['name']} ({destination_code})",
                    ],
                    hoverinfo="text",
                )
            )

            middle_index = len(route_lats) // 2

            fig.add_trace(
                go.Scattergeo(
                    lon=[route_lons[middle_index]],
                    lat=[route_lats[middle_index]],
                    mode="text",
                    text=["✈️"],
                    textfont={"size": 28},
                    name="Pesawat",
                    hoverinfo="skip",
                )
            )

    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        showcountries=True,
        showocean=True,
        showlakes=True,
        showrivers=True,
        lataxis_showgrid=True,
        lonaxis_showgrid=True,
    )

    fig.update_layout(
        height=560,
        margin={"r": 0, "t": 20, "l": 0, "b": 0},
        showlegend=True,
    )

    return fig


def render_globe(route: Optional[Dict] = None):
    st.subheader("🌍 Global Flight Route Map")

    if not route:
        st.caption(
            "Belum ada rute yang dipilih. Globe masih kosong dan bisa diputar."
        )
    else:
        st.caption(
            f"Menampilkan rute {route.get('origin')} menuju {route.get('destination')}."
        )

    fig = build_globe_figure(route)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )
