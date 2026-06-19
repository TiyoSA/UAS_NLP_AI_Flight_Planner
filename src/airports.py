AIRPORTS_BY_CITY = {
    "Jakarta": [
        {
            "code": "CGK",
            "name": "Bandara Internasional Soekarno-Hatta",
            "note": "Bandara utama Jakarta, lokasi di Tangerang, cocok untuk penerbangan domestik dan internasional."
        },
        {
            "code": "HLP",
            "name": "Bandara Halim Perdanakusuma",
            "note": "Lebih dekat ke pusat Jakarta, tetapi pilihan penerbangan bisa lebih terbatas."
        },
    ],
    "Bali / Denpasar": [
        {
            "code": "DPS",
            "name": "Bandara Internasional I Gusti Ngurah Rai",
            "note": "Bandara utama Bali untuk penerbangan domestik dan internasional."
        },
    ],
    "Pekanbaru": [
        {
            "code": "PKU",
            "name": "Bandara Sultan Syarif Kasim II",
            "note": "Bandara utama Pekanbaru."
        },
    ],
    "Batam": [
        {
            "code": "BTH",
            "name": "Bandara Hang Nadim",
            "note": "Bandara utama Batam."
        },
    ],
    "Medan": [
        {
            "code": "KNO",
            "name": "Bandara Internasional Kualanamu",
            "note": "Bandara utama Medan dan Sumatera Utara."
        },
    ],
    "Surabaya": [
        {
            "code": "SUB",
            "name": "Bandara Internasional Juanda",
            "note": "Bandara utama Surabaya."
        },
    ],
    "Yogyakarta": [
        {
            "code": "YIA",
            "name": "Yogyakarta International Airport",
            "note": "Bandara utama Yogyakarta yang lebih baru."
        },
        {
            "code": "JOG",
            "name": "Bandara Adisutjipto",
            "note": "Bandara lama Yogyakarta, layanan penerbangan bisa terbatas."
        },
    ],
    "Singapore": [
        {
            "code": "SIN",
            "name": "Singapore Changi Airport",
            "note": "Bandara utama Singapura."
        },
        {
            "code": "XSP",
            "name": "Seletar Airport",
            "note": "Bandara lebih kecil di Singapura, pilihan rute lebih terbatas."
        },
    ],
    "Kuala Lumpur": [
        {
            "code": "KUL",
            "name": "Kuala Lumpur International Airport",
            "note": "Bandara utama Kuala Lumpur."
        },
        {
            "code": "SZB",
            "name": "Sultan Abdul Aziz Shah Airport / Subang Airport",
            "note": "Lebih dekat ke kota, tetapi rute lebih terbatas."
        },
    ],
    "Bangkok": [
        {
            "code": "BKK",
            "name": "Suvarnabhumi Airport",
            "note": "Bandara internasional utama Bangkok."
        },
        {
            "code": "DMK",
            "name": "Don Mueang International Airport",
            "note": "Sering digunakan maskapai low-cost."
        },
    ],
    "Tokyo": [
        {
            "code": "HND",
            "name": "Tokyo Haneda Airport",
            "note": "Lebih dekat ke pusat Tokyo."
        },
        {
            "code": "NRT",
            "name": "Narita International Airport",
            "note": "Lebih jauh dari pusat Tokyo, tetapi banyak rute internasional."
        },
    ],
    "London": [
        {
            "code": "LHR",
            "name": "London Heathrow Airport",
            "note": "Bandara utama London, banyak rute internasional."
        },
        {
            "code": "LGW",
            "name": "London Gatwick Airport",
            "note": "Bandara besar alternatif London."
        },
        {
            "code": "STN",
            "name": "London Stansted Airport",
            "note": "Sering digunakan maskapai low-cost."
        },
        {
            "code": "LCY",
            "name": "London City Airport",
            "note": "Lebih dekat ke pusat kota, tetapi rute lebih terbatas."
        },
    ],
    "New York": [
        {
            "code": "JFK",
            "name": "John F. Kennedy International Airport",
            "note": "Bandara internasional utama New York."
        },
        {
            "code": "EWR",
            "name": "Newark Liberty International Airport",
            "note": "Alternatif utama New York di New Jersey."
        },
        {
            "code": "LGA",
            "name": "LaGuardia Airport",
            "note": "Lebih banyak untuk penerbangan domestik Amerika."
        },
    ],
}


CURRENCY_OPTIONS = {
    "IDR": "Indonesian Rupiah",
    "USD": "US Dollar",
    "SGD": "Singapore Dollar",
    "MYR": "Malaysian Ringgit",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
}


def get_city_names():
    return sorted(AIRPORTS_BY_CITY.keys())


def get_airports(city_name):
    return AIRPORTS_BY_CITY.get(city_name, [])


def format_airport_option(airport):
    return f'{airport["code"]} - {airport["name"]}'


def get_airport_by_label(city_name, label):
    airports = get_airports(city_name)

    for airport in airports:
        if format_airport_option(airport) == label:
            return airport

    return airports[0] if airports else {
        "code": "",
        "name": "",
        "note": "",
    }
