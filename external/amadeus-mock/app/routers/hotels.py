"""
Hotel List by City    — GET  /v1/reference-data/locations/hotels/by-city
Hotel Offers Search   — GET  /v3/shopping/hotel-offers
Hotel Order Create    — POST /v2/booking/hotel-orders
Hotel Order Retrieve  — GET  /v2/booking/hotel-orders/{orderId}
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.data.mock_data import CITY_TO_HOTEL_CITY, HOTELS
from app.dependencies import verify_token

router = APIRouter(tags=["Hotels"])

# In-memory order store
_hotel_orders: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _price_jitter(date_str: str, hotel_id: str) -> float:
    """Deterministic price variation per date+hotel."""
    seed = sum(ord(c) for c in (date_str + hotel_id))
    value = (seed * 2654435761) % (2**32)
    return 0.90 + (value % 1000) / 5000.0  # [0.90, 1.10]


def _build_hotel_offer(hotel: dict, room: dict, check_in: str, check_out: str, adults: int) -> dict:
    nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
    if nights < 1:
        nights = 1

    jitter = _price_jitter(check_in, hotel["hotelId"])
    nightly = round(room["basePrice"] * jitter, 2)
    base_total = round(nightly * nights, 2)
    tax_pct = 9.0
    taxes = round(base_total * tax_pct / 100, 2)
    grand_total = round(base_total + taxes, 2)

    offer_id = f"OFF{uuid.uuid5(uuid.NAMESPACE_DNS, hotel['hotelId'] + room['type'] + check_in).hex[:12].upper()}"

    # Cancellation deadline = 1 day before check-in
    cancel_dt = (datetime.strptime(check_in, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%dT23:59:00")

    return {
        "id": offer_id,
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "rateCode": "RAC",
        "rateFamilyEstimated": {"code": "PRO", "type": "P"},
        "category": "STANDARD",
        "description": {
            "lang": "EN",
            "text": room["description"],
        },
        "commission": {"percentage": "0"},
        "boardType": "ROOM_ONLY",
        "room": {
            "type": room["type"],
            "typeEstimated": {
                "category": room["type"],
                "beds": room["beds"],
                "bedType": room["bedType"],
            },
            "description": {
                "lang": "EN",
                "text": room["description"],
            },
        },
        "guests": {"adults": adults},
        "price": {
            "currency": "USD",
            "base": str(base_total),
            "total": str(grand_total),
            "taxes": [
                {
                    "code": "GST",
                    "amount": str(taxes),
                    "currency": "USD",
                    "percentage": str(tax_pct),
                    "included": False,
                    "description": "GOODS AND SERVICES TAX",
                    "pricingFrequency": "PER_STAY",
                    "pricingMode": "PER_PRODUCT",
                }
            ],
            "variations": {
                "average": {"base": str(nightly)},
                "changes": [
                    {
                        "startDate": check_in,
                        "endDate": check_out,
                        "base": str(nightly),
                    }
                ],
            },
        },
        "policies": {
            "cancellations": [
                {
                    "deadline": cancel_dt,
                    "description": {
                        "lang": "EN",
                        "text": f"Free cancellation before {cancel_dt}",
                    },
                }
            ],
            "guarantee": {
                "acceptedPayments": {
                    "creditCards": ["VI", "MC", "AX", "DC"],
                    "methods": ["CREDIT_CARD"],
                }
            },
            "paymentType": "GUARANTEE",
        },
        "self": f"/v3/shopping/hotel-offers/{offer_id}",
    }


def _hotel_to_list_entry(hotel: dict, city_code: str, country_code: str) -> dict:
    return {
        "type": "hotel",
        "hotelId": hotel["hotelId"],
        "dupeId": str(abs(hash(hotel["hotelId"])) % 1000000000),
        "name": hotel["name"],
        "cityCode": city_code,
        "countryCode": country_code,
        "iataCode": city_code,
        "address": hotel["address"],
        "geoCode": hotel["geoCode"],
        "distance": hotel["distance"],
        "amenities": hotel["amenities"],
        "rating": hotel["rating"],
        "lastUpdate": "2025-01-01T00:00:00",
    }


# ---------------------------------------------------------------------------
# GET /v1/reference-data/locations/hotels/by-city
# ---------------------------------------------------------------------------

@router.get("/v1/reference-data/locations/hotels/by-city")
def list_hotels_by_city(
    cityCode: str = Query(..., description="City or airport IATA code (e.g. SIN, LON)"),
    radius: int = Query(5, ge=0, le=300),
    radiusUnit: str = Query("KM"),
    hotelSource: str = Query("ALL"),
    _token: str = Depends(verify_token),
):
    city = cityCode.upper()
    hotel_city = CITY_TO_HOTEL_CITY.get(city, city)
    hotel_list = HOTELS.get(hotel_city, [])

    if not hotel_list:
        return {
            "data": [],
            "meta": {
                "count": 0,
                "links": {"self": f"/v1/reference-data/locations/hotels/by-city?cityCode={city}"},
            },
        }

    # Determine country code from first hotel entry
    country_code = hotel_list[0]["address"]["countryCode"]

    entries = [_hotel_to_list_entry(h, hotel_city, country_code) for h in hotel_list]

    return {
        "data": entries,
        "meta": {
            "count": len(entries),
            "links": {
                "self": f"/v1/reference-data/locations/hotels/by-city?cityCode={city}&radius={radius}&radiusUnit={radiusUnit}"
            },
        },
    }


# ---------------------------------------------------------------------------
# GET /v3/shopping/hotel-offers
# ---------------------------------------------------------------------------

@router.get("/v3/shopping/hotel-offers")
def search_hotel_offers(
    hotelIds: str = Query(..., description="Comma-separated hotel IDs"),
    adults: int = Query(1, ge=1, le=9),
    checkInDate: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    checkOutDate: str = Query(..., description="Check-out date (YYYY-MM-DD)"),
    roomQuantity: int = Query(1, ge=1, le=9),
    currency: str = Query("USD"),
    _token: str = Depends(verify_token),
):
    # Validate dates
    try:
        ci = datetime.strptime(checkInDate, "%Y-%m-%d")
        co = datetime.strptime(checkOutDate, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 477,
                        "title": "INVALID FORMAT",
                        "detail": "checkInDate or checkOutDate is not a valid YYYY-MM-DD date",
                    }
                ]
            },
        )

    if co <= ci:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 477,
                        "title": "INVALID FORMAT",
                        "detail": "checkOutDate must be after checkInDate",
                    }
                ]
            },
        )

    requested_ids = [h.strip().upper() for h in hotelIds.split(",")]

    # Build a flat lookup: hotelId → hotel dict
    hotel_lookup: dict[str, dict] = {}
    for city_hotels in HOTELS.values():
        for h in city_hotels:
            hotel_lookup[h["hotelId"]] = h

    results = []
    for hotel_id in requested_ids:
        hotel = hotel_lookup.get(hotel_id)
        if not hotel:
            # Return unavailable entry
            results.append({
                "type": "hotel-offers",
                "hotel": {
                    "type": "hotel",
                    "hotelId": hotel_id,
                    "name": hotel_id,
                    "cityCode": "UNK",
                },
                "available": False,
                "offers": [],
                "self": f"/v3/shopping/hotel-offers?hotelIds={hotel_id}",
            })
            continue

        offers = [
            _build_hotel_offer(hotel, room, checkInDate, checkOutDate, adults)
            for room in hotel["rooms"]
        ]

        city_code = hotel["address"].get("cityCode") or hotel["address"].get("cityName", "UNK")[:3].upper()
        # Get city from hotel city list key
        for ckey, clist in HOTELS.items():
            if any(h["hotelId"] == hotel_id for h in clist):
                city_code = ckey
                break

        results.append({
            "type": "hotel-offers",
            "hotel": {
                "type": "hotel",
                "hotelId": hotel["hotelId"],
                "name": hotel["name"],
                "cityCode": city_code,
                "countryCode": hotel["address"]["countryCode"],
                "rating": hotel["rating"],
                "address": hotel["address"],
                "amenities": hotel["amenities"],
                "geoCode": hotel["geoCode"],
            },
            "available": True,
            "offers": offers,
            "self": f"/v3/shopping/hotel-offers?hotelIds={hotel_id}&adults={adults}&checkInDate={checkInDate}&checkOutDate={checkOutDate}",
        })

    return {"data": results}


# ---------------------------------------------------------------------------
# GET /v3/shopping/hotel-offers/{offerId}
# ---------------------------------------------------------------------------

@router.get("/v3/shopping/hotel-offers/{offerId}")
def get_hotel_offer(
    offerId: str,
    _token: str = Depends(verify_token),
):
    # Search all rooms for the offer ID
    for city_hotels in HOTELS.values():
        for hotel in city_hotels:
            for room in hotel["rooms"]:
                offer_id = f"OFF{uuid.uuid5(uuid.NAMESPACE_DNS, hotel['hotelId'] + room['type']).hex[:12].upper()}"
                if offer_id == offerId.upper():
                    today = date.today()
                    check_in = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    check_out = (today + timedelta(days=10)).strftime("%Y-%m-%d")
                    offer = _build_hotel_offer(hotel, room, check_in, check_out, 1)
                    offer["id"] = offerId
                    return {"data": {"type": "hotel-offers", "hotel": {"hotelId": hotel["hotelId"], "name": hotel["name"]}, "offers": [offer]}}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "errors": [
                {
                    "status": 404,
                    "code": 1797,
                    "title": "NOT FOUND",
                    "detail": f"Hotel offer '{offerId}' not found",
                }
            ]
        },
    )


# ---------------------------------------------------------------------------
# POST /v2/booking/hotel-orders
# ---------------------------------------------------------------------------

@router.post("/v2/booking/hotel-orders", status_code=status.HTTP_201_CREATED)
def create_hotel_order(
    body: dict,
    _token: str = Depends(verify_token),
):
    if "data" not in body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 32171,
                        "title": "MANDATORY DATA MISSING",
                        "detail": "Missing mandatory field: data",
                    }
                ]
            },
        )

    order_data = body["data"]
    hotel_offers = order_data.get("hotelOffers", [])
    guests = order_data.get("guests", [])

    if not hotel_offers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 32171,
                        "title": "MANDATORY DATA MISSING",
                        "detail": "hotelOffers must not be empty",
                    }
                ]
            },
        )

    order_id = f"HORDER{uuid.uuid4().hex[:8].upper()}"
    confirmation = f"CONF{uuid.uuid4().hex[:6].upper()}"

    order = {
        "type": "hotel-order",
        "id": order_id,
        "hotelOffers": hotel_offers,
        "guests": guests,
        "payments": order_data.get("payments", []),
        "associatedRecords": [
            {
                "reference": confirmation,
                "originSystemCode": "GDS",
            }
        ],
    }

    _hotel_orders[order_id] = order

    return {
        "data": {
            "type": "hotel-order",
            "id": order_id,
            "hotelBookings": [
                {
                    "type": "hotel-booking",
                    "id": f"BKG{uuid.uuid4().hex[:8].upper()}",
                    "bookingStatus": "CONFIRMED",
                    "confRoomLists": [{"confirmationId": confirmation}],
                    "hotelOffer": offer,
                    "hotel": offer.get("hotel", {}),
                    "guests": guests,
                }
                for offer in hotel_offers
            ],
            "associatedRecords": [
                {
                    "reference": confirmation,
                    "originSystemCode": "GDS",
                }
            ],
        }
    }


# ---------------------------------------------------------------------------
# GET /v2/booking/hotel-orders/{orderId}
# ---------------------------------------------------------------------------

@router.get("/v2/booking/hotel-orders/{orderId}")
def get_hotel_order(
    orderId: str,
    _token: str = Depends(verify_token),
):
    order = _hotel_orders.get(orderId)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errors": [
                    {
                        "status": 404,
                        "code": 1797,
                        "title": "NOT FOUND",
                        "detail": f"Hotel order '{orderId}' not found",
                    }
                ]
            },
        )
    return {"data": order}
