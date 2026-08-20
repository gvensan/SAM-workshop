"""
Static mock data: routes, carriers, aircraft, airports, and hotels.
All prices are base prices — the router adds per-class multipliers and
a small deterministic jitter based on the travel date.
"""

# ------------------------------------------------------------------
# Reference dictionaries (returned in flight offer "dictionaries")
# ------------------------------------------------------------------

CARRIERS = {
    "SQ": "SINGAPORE AIRLINES",
    "QF": "QANTAS",
    "BA": "BRITISH AIRWAYS",
    "EK": "EMIRATES",
    "AA": "AMERICAN AIRLINES",
    "UA": "UNITED AIRLINES",
    "LH": "LUFTHANSA",
    "AF": "AIR FRANCE",
    "CX": "CATHAY PACIFIC",
    "JL": "JAPAN AIRLINES",
    "TK": "TURKISH AIRLINES",
    "NH": "ANA - ALL NIPPON AIRWAYS",
}

AIRCRAFT = {
    "359": "AIRBUS A350-900",
    "77W": "BOEING 777-300ER",
    "789": "BOEING 787-9",
    "388": "AIRBUS A380-800",
    "321": "AIRBUS A321",
    "738": "BOEING 737-800",
    "320": "AIRBUS A320",
    "744": "BOEING 747-400",
}

AIRPORTS = {
    "SIN": {"cityCode": "SIN", "countryCode": "SG", "name": "CHANGI AIRPORT"},
    "LHR": {"cityCode": "LON", "countryCode": "GB", "name": "HEATHROW AIRPORT"},
    "JFK": {"cityCode": "NYC", "countryCode": "US", "name": "JOHN F KENNEDY INTL"},
    "LAX": {"cityCode": "LAX", "countryCode": "US", "name": "LOS ANGELES INTL"},
    "SYD": {"cityCode": "SYD", "countryCode": "AU", "name": "SYDNEY KINGSFORD SMITH"},
    "DXB": {"cityCode": "DXB", "countryCode": "AE", "name": "DUBAI INTL"},
    "CDG": {"cityCode": "PAR", "countryCode": "FR", "name": "CHARLES DE GAULLE"},
    "HND": {"cityCode": "TYO", "countryCode": "JP", "name": "TOKYO HANEDA"},
    "NRT": {"cityCode": "TYO", "countryCode": "JP", "name": "NARITA INTL"},
    "BKK": {"cityCode": "BKK", "countryCode": "TH", "name": "SUVARNABHUMI AIRPORT"},
    "HKG": {"cityCode": "HKG", "countryCode": "HK", "name": "HONG KONG INTL"},
    "FRA": {"cityCode": "FRA", "countryCode": "DE", "name": "FRANKFURT MAIN"},
}

# ------------------------------------------------------------------
# Route definitions
# Each entry: list of flight options per route.
# Fields: carrier, flightNo, aircraft, departureTime (HH:MM),
#         durationMinutes, stops (list of stop dicts), terminal_dep, terminal_arr
# Base prices (USD) by cabin: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
# ------------------------------------------------------------------

ROUTES = {
    ("SIN", "LHR"): {
        "options": [
            {
                "carrier": "SQ",
                "flightNo": "SQ317",
                "aircraft": "359",
                "departureTime": "01:30",
                "durationMinutes": 810,  # 13h30m
                "stops": [],
                "terminal_dep": "3",
                "terminal_arr": "2",
                "seats": 9,
            },
            {
                "carrier": "BA",
                "flightNo": "BA12",
                "aircraft": "77W",
                "departureTime": "23:55",
                "durationMinutes": 780,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "5",
                "seats": 4,
            },
            {
                "carrier": "EK",
                "flightNo": "EK431",
                "aircraft": "388",
                "departureTime": "03:45",
                "durationMinutes": 1110,  # via DXB
                "stops": [
                    {
                        "iataCode": "DXB",
                        "duration": "PT2H15M",
                        "arrivalAt": "06:30",
                        "departureAt": "08:45",
                        "terminal": "3",
                    }
                ],
                "terminal_dep": "2",
                "terminal_arr": "3",
                "seats": 15,
            },
        ],
        "basePrices": {
            "ECONOMY": 950,
            "PREMIUM_ECONOMY": 1800,
            "BUSINESS": 4200,
            "FIRST": 8500,
        },
    },
    ("SIN", "SYD"): {
        "options": [
            {
                "carrier": "SQ",
                "flightNo": "SQ221",
                "aircraft": "359",
                "departureTime": "08:20",
                "durationMinutes": 465,  # 7h45m
                "stops": [],
                "terminal_dep": "3",
                "terminal_arr": "1",
                "seats": 9,
            },
            {
                "carrier": "QF",
                "flightNo": "QF82",
                "aircraft": "789",
                "departureTime": "16:00",
                "durationMinutes": 480,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "1",
                "seats": 6,
            },
        ],
        "basePrices": {
            "ECONOMY": 620,
            "PREMIUM_ECONOMY": 1200,
            "BUSINESS": 3100,
            "FIRST": 6500,
        },
    },
    ("JFK", "LAX"): {
        "options": [
            {
                "carrier": "AA",
                "flightNo": "AA1",
                "aircraft": "321",
                "departureTime": "07:00",
                "durationMinutes": 360,
                "stops": [],
                "terminal_dep": "8",
                "terminal_arr": "4",
                "seats": 20,
            },
            {
                "carrier": "UA",
                "flightNo": "UA177",
                "aircraft": "738",
                "departureTime": "10:30",
                "durationMinutes": 355,
                "stops": [],
                "terminal_dep": "7",
                "terminal_arr": "7",
                "seats": 12,
            },
            {
                "carrier": "AA",
                "flightNo": "AA3",
                "aircraft": "738",
                "departureTime": "18:00",
                "durationMinutes": 375,
                "stops": [],
                "terminal_dep": "8",
                "terminal_arr": "4",
                "seats": 8,
            },
        ],
        "basePrices": {
            "ECONOMY": 280,
            "PREMIUM_ECONOMY": 520,
            "BUSINESS": 1100,
            "FIRST": 2200,
        },
    },
    ("LHR", "CDG"): {
        "options": [
            {
                "carrier": "BA",
                "flightNo": "BA306",
                "aircraft": "320",
                "departureTime": "06:55",
                "durationMinutes": 75,
                "stops": [],
                "terminal_dep": "5",
                "terminal_arr": "2",
                "seats": 30,
            },
            {
                "carrier": "AF",
                "flightNo": "AF1681",
                "aircraft": "320",
                "departureTime": "09:30",
                "durationMinutes": 80,
                "stops": [],
                "terminal_dep": "2",
                "terminal_arr": "2F",
                "seats": 22,
            },
        ],
        "basePrices": {
            "ECONOMY": 120,
            "PREMIUM_ECONOMY": 230,
            "BUSINESS": 550,
            "FIRST": 1100,
        },
    },
    ("DXB", "SIN"): {
        "options": [
            {
                "carrier": "EK",
                "flightNo": "EK432",
                "aircraft": "388",
                "departureTime": "09:30",
                "durationMinutes": 420,
                "stops": [],
                "terminal_dep": "3",
                "terminal_arr": "1",
                "seats": 11,
            },
            {
                "carrier": "SQ",
                "flightNo": "SQ496",
                "aircraft": "77W",
                "departureTime": "14:00",
                "durationMinutes": 435,
                "stops": [],
                "terminal_dep": "2",
                "terminal_arr": "3",
                "seats": 7,
            },
        ],
        "basePrices": {
            "ECONOMY": 480,
            "PREMIUM_ECONOMY": 920,
            "BUSINESS": 2400,
            "FIRST": 5200,
        },
    },
    ("SIN", "HND"): {
        "options": [
            {
                "carrier": "SQ",
                "flightNo": "SQ637",
                "aircraft": "789",
                "departureTime": "00:05",
                "durationMinutes": 420,
                "stops": [],
                "terminal_dep": "3",
                "terminal_arr": "3",
                "seats": 9,
            },
            {
                "carrier": "JL",
                "flightNo": "JL37",
                "aircraft": "789",
                "departureTime": "11:20",
                "durationMinutes": 415,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "3",
                "seats": 14,
            },
        ],
        "basePrices": {
            "ECONOMY": 550,
            "PREMIUM_ECONOMY": 1050,
            "BUSINESS": 2800,
            "FIRST": 6000,
        },
    },
    ("SIN", "BKK"): {
        "options": [
            {
                "carrier": "SQ",
                "flightNo": "SQ705",
                "aircraft": "320",
                "departureTime": "07:30",
                "durationMinutes": 150,
                "stops": [],
                "terminal_dep": "3",
                "terminal_arr": "2",
                "seats": 25,
            },
            {
                "carrier": "TK",
                "flightNo": "TK67",
                "aircraft": "321",
                "departureTime": "14:15",
                "durationMinutes": 165,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "2",
                "seats": 18,
            },
        ],
        "basePrices": {
            "ECONOMY": 180,
            "PREMIUM_ECONOMY": 340,
            "BUSINESS": 820,
            "FIRST": 1800,
        },
    },
    ("HKG", "LHR"): {
        "options": [
            {
                "carrier": "CX",
                "flightNo": "CX251",
                "aircraft": "77W",
                "departureTime": "23:50",
                "durationMinutes": 735,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "3",
                "seats": 8,
            },
            {
                "carrier": "BA",
                "flightNo": "BA31",
                "aircraft": "77W",
                "departureTime": "12:10",
                "durationMinutes": 750,
                "stops": [],
                "terminal_dep": "1",
                "terminal_arr": "5",
                "seats": 5,
            },
        ],
        "basePrices": {
            "ECONOMY": 780,
            "PREMIUM_ECONOMY": 1500,
            "BUSINESS": 3800,
            "FIRST": 7800,
        },
    },
}

# Cabin class multipliers (applied on top of base price)
CABIN_MULTIPLIERS = {
    "ECONOMY": 1.0,
    "PREMIUM_ECONOMY": 1.9,
    "BUSINESS": 4.4,
    "FIRST": 9.0,
}

# Fare basis codes per cabin
FARE_BASIS = {
    "ECONOMY": {"code": "YOWSGB", "branded": "LITE", "class": "Y"},
    "PREMIUM_ECONOMY": {"code": "WOWSGB", "branded": "FLEX", "class": "W"},
    "BUSINESS": {"code": "COWSGB", "branded": "BUSINESS", "class": "C"},
    "FIRST": {"code": "FOWSGB", "branded": "SUITES", "class": "F"},
}

CHECKED_BAGS = {
    "ECONOMY": {"quantity": 1},
    "PREMIUM_ECONOMY": {"quantity": 2},
    "BUSINESS": {"quantity": 2},
    "FIRST": {"quantity": 3},
}

# ------------------------------------------------------------------
# Hotel data by city code
# ------------------------------------------------------------------

HOTELS = {
    "SIN": [
        {
            "hotelId": "ADSINFL1",
            "name": "THE FULLERTON HOTEL SINGAPORE",
            "rating": "5",
            "address": {
                "lines": ["1 FULLERTON SQUARE"],
                "postalCode": "049178",
                "cityName": "SINGAPORE",
                "countryCode": "SG",
            },
            "geoCode": {"latitude": 1.2864, "longitude": 103.8534},
            "distance": {"value": 0.9, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "CONCIERGE"],
            "rooms": [
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 420, "description": "Deluxe Room with heritage courtyard view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 850, "description": "Grand Suite with city and bay views"},
            ],
        },
        {
            "hotelId": "ADSINMA1",
            "name": "MARINA BAY SANDS HOTEL",
            "rating": "5",
            "address": {
                "lines": ["10 BAYFRONT AVENUE"],
                "postalCode": "018956",
                "cityName": "SINGAPORE",
                "countryCode": "SG",
            },
            "geoCode": {"latitude": 1.2839, "longitude": 103.8607},
            "distance": {"value": 1.2, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "CASINO"],
            "rooms": [
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 480, "description": "Deluxe Room with Marina Bay view"},
                {"type": "PREMIER_ROOM", "beds": 1, "bedType": "KING", "basePrice": 650, "description": "Premier Room with Sands SkyPark access"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 1200, "description": "Chairman Suite with panoramic city views"},
            ],
        },
        {
            "hotelId": "ADSINRA1",
            "name": "RAFFLES HOTEL SINGAPORE",
            "rating": "5",
            "address": {
                "lines": ["1 BEACH ROAD"],
                "postalCode": "189673",
                "cityName": "SINGAPORE",
                "countryCode": "SG",
            },
            "geoCode": {"latitude": 1.2952, "longitude": 103.8527},
            "distance": {"value": 0.5, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BAR"],
            "rooms": [
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 900, "description": "Courtyard Suite with colonial garden view"},
                {"type": "SUITE", "beds": 2, "bedType": "DOUBLE", "basePrice": 750, "description": "Palm Court Suite with tropical garden views"},
            ],
        },
        {
            "hotelId": "ADSINCO1",
            "name": "COMO METROPOLITAN SINGAPORE",
            "rating": "5",
            "address": {
                "lines": ["1 UNITY STREET"],
                "postalCode": "237983",
                "cityName": "SINGAPORE",
                "countryCode": "SG",
            },
            "geoCode": {"latitude": 1.3025, "longitude": 103.8379},
            "distance": {"value": 2.1, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "QUEEN", "basePrice": 280, "description": "Superior Room with city views"},
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 380, "description": "Deluxe Room with balcony"},
            ],
        },
        {
            "hotelId": "ADSINHI1",
            "name": "HILTON SINGAPORE ORCHARD",
            "rating": "5",
            "address": {
                "lines": ["333 ORCHARD ROAD"],
                "postalCode": "238867",
                "cityName": "SINGAPORE",
                "countryCode": "SG",
            },
            "geoCode": {"latitude": 1.3041, "longitude": 103.8321},
            "distance": {"value": 2.5, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "KING", "basePrice": 220, "description": "Deluxe Room"},
                {"type": "DELUXE_ROOM", "beds": 2, "bedType": "DOUBLE", "basePrice": 260, "description": "Twin Room"},
            ],
        },
    ],
    "LON": [
        {
            "hotelId": "ADLONSA1",
            "name": "THE SAVOY HOTEL",
            "rating": "5",
            "address": {
                "lines": ["STRAND"],
                "postalCode": "WC2R 0EU",
                "cityName": "LONDON",
                "countryCode": "GB",
            },
            "geoCode": {"latitude": 51.5107, "longitude": -0.1204},
            "distance": {"value": 1.1, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "POOL"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "KING", "basePrice": 520, "description": "Classic Room with river view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 1400, "description": "River Suite"},
            ],
        },
        {
            "hotelId": "ADLONCL1",
            "name": "THE CLARIDGE'S",
            "rating": "5",
            "address": {
                "lines": ["BROOK STREET", "MAYFAIR"],
                "postalCode": "W1K 4HR",
                "cityName": "LONDON",
                "countryCode": "GB",
            },
            "geoCode": {"latitude": 51.5122, "longitude": -0.1480},
            "distance": {"value": 0.8, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BAR"],
            "rooms": [
                {"type": "CLASSIC_ROOM", "beds": 1, "bedType": "KING", "basePrice": 680, "description": "Classic Room with Art Deco design"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 2200, "description": "Royal Suite"},
            ],
        },
        {
            "hotelId": "ADLONHI1",
            "name": "HILTON LONDON METROPOLE",
            "rating": "4",
            "address": {
                "lines": ["225 EDGWARE ROAD"],
                "postalCode": "W2 1JU",
                "cityName": "LONDON",
                "countryCode": "GB",
            },
            "geoCode": {"latitude": 51.5171, "longitude": -0.1676},
            "distance": {"value": 3.2, "unit": "KM"},
            "amenities": ["FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "DOUBLE", "basePrice": 180, "description": "Standard Room"},
                {"type": "EXECUTIVE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 260, "description": "Executive Room with lounge access"},
            ],
        },
    ],
    "NYC": [
        {
            "hotelId": "ADNYCPL1",
            "name": "THE PLAZA NEW YORK",
            "rating": "5",
            "address": {
                "lines": ["768 5TH AVENUE"],
                "postalCode": "10019",
                "cityName": "NEW YORK",
                "countryCode": "US",
            },
            "geoCode": {"latitude": 40.7644, "longitude": -73.9747},
            "distance": {"value": 0.5, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BAR"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "KING", "basePrice": 750, "description": "Classic Room with Central Park view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 2500, "description": "Eloise Suite"},
            ],
        },
        {
            "hotelId": "ADNYCMA1",
            "name": "NEW YORK MARRIOTT MARQUIS",
            "rating": "4",
            "address": {
                "lines": ["1535 BROADWAY"],
                "postalCode": "10036",
                "cityName": "NEW YORK",
                "countryCode": "US",
            },
            "geoCode": {"latitude": 40.7580, "longitude": -73.9855},
            "distance": {"value": 1.2, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "KING", "basePrice": 380, "description": "Times Square View Room"},
                {"type": "DELUXE_ROOM", "beds": 2, "bedType": "DOUBLE", "basePrice": 420, "description": "Double Room City View"},
            ],
        },
        {
            "hotelId": "ADNYCST1",
            "name": "ST. REGIS NEW YORK",
            "rating": "5",
            "address": {
                "lines": ["2 EAST 55TH STREET"],
                "postalCode": "10022",
                "cityName": "NEW YORK",
                "countryCode": "US",
            },
            "geoCode": {"latitude": 40.7613, "longitude": -73.9730},
            "distance": {"value": 0.3, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BUTLER_SERVICE"],
            "rooms": [
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 920, "description": "Deluxe Room"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 3200, "description": "Presidential Suite"},
            ],
        },
    ],
    "SYD": [
        {
            "hotelId": "ADSYDOP1",
            "name": "PARK HYATT SYDNEY",
            "rating": "5",
            "address": {
                "lines": ["7 HICKSON ROAD", "THE ROCKS"],
                "postalCode": "2000",
                "cityName": "SYDNEY",
                "countryCode": "AU",
            },
            "geoCode": {"latitude": -33.8567, "longitude": 151.2099},
            "distance": {"value": 0.4, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "PARK_ROOM", "beds": 1, "bedType": "KING", "basePrice": 680, "description": "Park Room with Opera House view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 1800, "description": "Opera Suite"},
            ],
        },
        {
            "hotelId": "ADSYDSH1",
            "name": "SHERATON GRAND SYDNEY HYDE PARK",
            "rating": "5",
            "address": {
                "lines": ["161 ELIZABETH STREET"],
                "postalCode": "2000",
                "cityName": "SYDNEY",
                "countryCode": "AU",
            },
            "geoCode": {"latitude": -33.8723, "longitude": 151.2099},
            "distance": {"value": 1.8, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "STANDARD_ROOM", "beds": 1, "bedType": "KING", "basePrice": 290, "description": "Superior Room"},
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 380, "description": "Deluxe Room with park view"},
            ],
        },
    ],
    "DXB": [
        {
            "hotelId": "ADDXBBR1",
            "name": "BURJ AL ARAB JUMEIRAH",
            "rating": "5",
            "address": {
                "lines": ["JUMEIRAH BEACH ROAD"],
                "postalCode": "74925",
                "cityName": "DUBAI",
                "countryCode": "AE",
            },
            "geoCode": {"latitude": 25.1413, "longitude": 55.1853},
            "distance": {"value": 15.0, "unit": "KM"},
            "amenities": ["PRIVATE_BEACH", "SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "HELIPAD"],
            "rooms": [
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 2800, "description": "Deluxe Suite with Arabian Gulf view"},
                {"type": "ROYAL_SUITE", "beds": 1, "bedType": "KING", "basePrice": 8500, "description": "Royal Suite with private butler"},
            ],
        },
        {
            "hotelId": "ADDXBAT1",
            "name": "ATLANTIS THE PALM",
            "rating": "5",
            "address": {
                "lines": ["CRESCENT ROAD", "THE PALM"],
                "postalCode": "74915",
                "cityName": "DUBAI",
                "countryCode": "AE",
            },
            "geoCode": {"latitude": 25.1303, "longitude": 55.1171},
            "distance": {"value": 24.0, "unit": "KM"},
            "amenities": ["WATERPARK", "PRIVATE_BEACH", "SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "CASINO"],
            "rooms": [
                {"type": "CORAL_ROOM", "beds": 1, "bedType": "KING", "basePrice": 480, "description": "Coral Room with lagoon view"},
                {"type": "TERRACE_SUITE", "beds": 1, "bedType": "KING", "basePrice": 1100, "description": "Terrace Suite with Palm view"},
            ],
        },
        {
            "hotelId": "ADDXBAD1",
            "name": "ADDRESS DOWNTOWN DUBAI",
            "rating": "5",
            "address": {
                "lines": ["DOWNTOWN DUBAI"],
                "postalCode": "75888",
                "cityName": "DUBAI",
                "countryCode": "AE",
            },
            "geoCode": {"latitude": 25.1972, "longitude": 55.2744},
            "distance": {"value": 1.2, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "PREMIER_ROOM", "beds": 1, "bedType": "KING", "basePrice": 380, "description": "Premier Room with Burj Khalifa view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 950, "description": "Suite with panoramic views"},
            ],
        },
    ],
    "PAR": [
        {
            "hotelId": "ADPARRI1",
            "name": "THE RITZ PARIS",
            "rating": "5",
            "address": {
                "lines": ["15 PLACE VENDÔME"],
                "postalCode": "75001",
                "cityName": "PARIS",
                "countryCode": "FR",
            },
            "geoCode": {"latitude": 48.8687, "longitude": 2.3303},
            "distance": {"value": 0.6, "unit": "KM"},
            "amenities": ["SPA", "SWIMMING_POOL", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BAR"],
            "rooms": [
                {"type": "CLASSIC_ROOM", "beds": 1, "bedType": "KING", "basePrice": 1100, "description": "Classic Room"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 4500, "description": "Imperial Suite"},
            ],
        },
        {
            "hotelId": "ADPARLE1",
            "name": "LE MEURICE",
            "rating": "5",
            "address": {
                "lines": ["228 RUE DE RIVOLI"],
                "postalCode": "75001",
                "cityName": "PARIS",
                "countryCode": "FR",
            },
            "geoCode": {"latitude": 48.8645, "longitude": 2.3300},
            "distance": {"value": 0.4, "unit": "KM"},
            "amenities": ["SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 950, "description": "Deluxe Room with garden view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 3800, "description": "Belle Etoile Suite"},
            ],
        },
    ],
    "TYO": [
        {
            "hotelId": "ADTYOPA1",
            "name": "PARK HYATT TOKYO",
            "rating": "5",
            "address": {
                "lines": ["3-7-1-2 NISHI-SHINJUKU"],
                "postalCode": "163-1055",
                "cityName": "TOKYO",
                "countryCode": "JP",
            },
            "geoCode": {"latitude": 35.6877, "longitude": 139.6902},
            "distance": {"value": 8.0, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT", "BAR"],
            "rooms": [
                {"type": "PARK_ROOM", "beds": 1, "bedType": "KING", "basePrice": 620, "description": "Park Room with Mount Fuji view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 2100, "description": "Presidential Suite"},
            ],
        },
        {
            "hotelId": "ADTYOMA1",
            "name": "THE PALACE HOTEL TOKYO",
            "rating": "5",
            "address": {
                "lines": ["1-1-1 MARUNOUCHI"],
                "postalCode": "100-0005",
                "cityName": "TOKYO",
                "countryCode": "JP",
            },
            "geoCode": {"latitude": 35.6855, "longitude": 139.7594},
            "distance": {"value": 1.5, "unit": "KM"},
            "amenities": ["SWIMMING_POOL", "SPA", "FITNESS_CENTER", "WIFI", "RESTAURANT"],
            "rooms": [
                {"type": "DELUXE_ROOM", "beds": 1, "bedType": "KING", "basePrice": 540, "description": "Deluxe Room with Imperial Palace view"},
                {"type": "SUITE", "beds": 1, "bedType": "KING", "basePrice": 1600, "description": "Palace Suite"},
            ],
        },
    ],
}

# City code aliases (airport → city hotel lookup)
CITY_TO_HOTEL_CITY = {
    "SIN": "SIN",
    "LHR": "LON",
    "LON": "LON",
    "JFK": "NYC",
    "LAX": "LAX",
    "NYC": "NYC",
    "SYD": "SYD",
    "DXB": "DXB",
    "CDG": "PAR",
    "PAR": "PAR",
    "HND": "TYO",
    "NRT": "TYO",
    "TYO": "TYO",
    "BKK": "BKK",
    "HKG": "HKG",
    "FRA": "FRA",
}
