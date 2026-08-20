"""
Flight Offers Search  — GET  /v2/shopping/flight-offers
Flight Order Create   — POST /v1/booking/flight-orders
Flight Order Retrieve — GET  /v1/booking/flight-orders/{orderId}
"""

import math
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.data.mock_data import (
    AIRCRAFT,
    AIRPORTS,
    CABIN_MULTIPLIERS,
    CARRIERS,
    CHECKED_BAGS,
    FARE_BASIS,
    ROUTES,
)
from app.dependencies import verify_token

router = APIRouter(tags=["Flights"])

# In-memory order store
_flight_orders: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_minutes(base_time: str, date: str, minutes: int) -> str:
    """Given HH:MM and a YYYY-MM-DD date, return ISO datetime after +minutes."""
    dt = datetime.strptime(f"{date}T{base_time}", "%Y-%m-%dT%H:%M")
    result = dt + timedelta(minutes=minutes)
    return result.strftime("%Y-%m-%dT%H:%M:00")


def _price_jitter(date_str: str, carrier: str, cabin: str) -> float:
    """
    Returns a deterministic multiplier in [0.85, 1.20] so the same
    date always gives the same price but different dates differ.
    """
    seed = sum(ord(c) for c in (date_str + carrier + cabin))
    # Pseudo-random via simple hash — repeatable, not truly random
    value = (seed * 2654435761) % (2**32)
    return 0.85 + (value % 1000) / 2857.0  # maps [0,999] → [0.85, 1.20]


def _build_offer(
    offer_id: int,
    segment_id_start: int,
    option: dict,
    dep_code: str,
    arr_code: str,
    dep_date: str,
    cabin: str,
    adults: int,
    base_price: float,
    return_date: Optional[str] = None,
) -> tuple[dict, int]:
    """Build a single flight-offer dict. Returns (offer, next_segment_id)."""

    jitter = _price_jitter(dep_date, option["carrier"], cabin)
    unit_price = round(base_price * jitter, 2)
    tax = round(unit_price * 0.12, 2)
    total = round((unit_price + tax) * adults, 2)

    segments = []
    seg_id = segment_id_start

    # Outbound itinerary
    out_segments = []
    stops = option.get("stops", [])

    if not stops:
        # Direct flight
        arr_at = _add_minutes(option["departureTime"], dep_date, option["durationMinutes"])
        out_segments.append({
            "departure": {
                "iataCode": dep_code,
                "terminal": option.get("terminal_dep", "1"),
                "at": f"{dep_date}T{option['departureTime']}:00",
            },
            "arrival": {
                "iataCode": arr_code,
                "terminal": option.get("terminal_arr", "1"),
                "at": arr_at,
            },
            "carrierCode": option["carrier"],
            "number": option["flightNo"].replace(option["carrier"], ""),
            "aircraft": {"code": option["aircraft"]},
            "operating": {"carrierCode": option["carrier"]},
            "duration": f"PT{option['durationMinutes'] // 60}H{option['durationMinutes'] % 60}M",
            "id": str(seg_id),
            "numberOfStops": 0,
            "blacklistedInEU": False,
        })
        seg_id += 1
    else:
        # Connecting flight — build leg 1 and leg 2
        stop = stops[0]
        # Leg 1: origin → stopover
        leg1_mins = int(option["durationMinutes"] * 0.45)
        arr1_at = _add_minutes(option["departureTime"], dep_date, leg1_mins)
        out_segments.append({
            "departure": {
                "iataCode": dep_code,
                "terminal": option.get("terminal_dep", "1"),
                "at": f"{dep_date}T{option['departureTime']}:00",
            },
            "arrival": {
                "iataCode": stop["iataCode"],
                "terminal": stop.get("terminal", "1"),
                "at": arr1_at,
            },
            "carrierCode": option["carrier"],
            "number": option["flightNo"].replace(option["carrier"], ""),
            "aircraft": {"code": option["aircraft"]},
            "operating": {"carrierCode": option["carrier"]},
            "duration": f"PT{leg1_mins // 60}H{leg1_mins % 60}M",
            "id": str(seg_id),
            "numberOfStops": 0,
            "blacklistedInEU": False,
        })
        seg_id += 1

        # Leg 2: stopover → destination
        leg2_mins = option["durationMinutes"] - leg1_mins - 135  # minus layover
        # departure of leg 2
        stopover_dep_dt = datetime.strptime(arr1_at, "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=135)
        stopover_dep_str = stopover_dep_dt.strftime("%Y-%m-%dT%H:%M:00")
        arr2_dt = stopover_dep_dt + timedelta(minutes=leg2_mins)
        arr2_str = arr2_dt.strftime("%Y-%m-%dT%H:%M:00")

        out_segments.append({
            "departure": {
                "iataCode": stop["iataCode"],
                "terminal": stop.get("terminal", "1"),
                "at": stopover_dep_str,
            },
            "arrival": {
                "iataCode": arr_code,
                "terminal": option.get("terminal_arr", "1"),
                "at": arr2_str,
            },
            "carrierCode": option["carrier"],
            "number": str(int(option["flightNo"].replace(option["carrier"], "")) + 1),
            "aircraft": {"code": option["aircraft"]},
            "operating": {"carrierCode": option["carrier"]},
            "duration": f"PT{leg2_mins // 60}H{leg2_mins % 60}M",
            "id": str(seg_id),
            "numberOfStops": 0,
            "blacklistedInEU": False,
        })
        seg_id += 1

    segments.extend(out_segments)
    itineraries = [
        {
            "duration": f"PT{option['durationMinutes'] // 60}H{option['durationMinutes'] % 60}M",
            "segments": out_segments,
        }
    ]

    # Return leg (if requested)
    return_segments = []
    if return_date:
        # Simple reverse flight — same carrier, aircraft, ~same duration
        ret_dep_time = option["departureTime"]  # reuse same time slot
        ret_arr_at = _add_minutes(ret_dep_time, return_date, option["durationMinutes"])
        return_segments.append({
            "departure": {
                "iataCode": arr_code,
                "terminal": option.get("terminal_arr", "1"),
                "at": f"{return_date}T{ret_dep_time}:00",
            },
            "arrival": {
                "iataCode": dep_code,
                "terminal": option.get("terminal_dep", "1"),
                "at": ret_arr_at,
            },
            "carrierCode": option["carrier"],
            "number": str(int(option["flightNo"].replace(option["carrier"], "")) + 100),
            "aircraft": {"code": option["aircraft"]},
            "operating": {"carrierCode": option["carrier"]},
            "duration": f"PT{option['durationMinutes'] // 60}H{option['durationMinutes'] % 60}M",
            "id": str(seg_id),
            "numberOfStops": 0,
            "blacklistedInEU": False,
        })
        seg_id += 1
        itineraries.append({
            "duration": f"PT{option['durationMinutes'] // 60}H{option['durationMinutes'] % 60}M",
            "segments": return_segments,
        })

    segments.extend(return_segments)

    fare = FARE_BASIS[cabin]
    all_seg_ids = [s["id"] for s in segments]

    fare_details = [
        {
            "segmentId": sid,
            "cabin": cabin,
            "fareBasis": fare["code"],
            "brandedFare": fare["branded"],
            "class": fare["class"],
            "includedCheckedBags": CHECKED_BAGS[cabin],
        }
        for sid in all_seg_ids
    ]

    # Last ticketing date = departure date - 3 days
    dep_dt = datetime.strptime(dep_date, "%Y-%m-%d")
    last_ticket = (dep_dt - timedelta(days=3)).strftime("%Y-%m-%d")

    offer = {
        "type": "flight-offer",
        "id": str(offer_id),
        "source": "GDS",
        "instantTicketingRequired": False,
        "nonHomogeneous": False,
        "oneWay": return_date is None,
        "lastTicketingDate": last_ticket,
        "lastTicketingDateTime": f"{last_ticket}T23:59:00",
        "numberOfBookableSeats": option.get("seats", 9),
        "itineraries": itineraries,
        "price": {
            "currency": "USD",
            "total": str(total),
            "base": str(round(unit_price * adults, 2)),
            "fees": [{"amount": str(round(tax * adults, 2)), "type": "SUPPLIER"}],
            "grandTotal": str(total),
        },
        "pricingOptions": {
            "fareType": ["PUBLISHED"],
            "includedCheckedBagsOnly": True,
        },
        "validatingAirlineCodes": [option["carrier"]],
        "travelerPricings": [
            {
                "travelerId": str(i + 1),
                "fareOption": "STANDARD",
                "travelerType": "ADULT",
                "price": {
                    "currency": "USD",
                    "total": str(round(unit_price + tax, 2)),
                    "base": str(unit_price),
                    "taxes": [
                        {"amount": str(round(tax * 0.6, 2)), "code": "YR"},
                        {"amount": str(round(tax * 0.4, 2)), "code": "YQ"},
                    ],
                },
                "fareDetailsBySegment": fare_details,
            }
            for i in range(adults)
        ],
    }

    return offer, seg_id


# ---------------------------------------------------------------------------
# GET /v2/shopping/flight-offers
# ---------------------------------------------------------------------------

@router.get("/v2/shopping/flight-offers")
def search_flight_offers(
    originLocationCode: str = Query(..., description="Origin airport IATA code"),
    destinationLocationCode: str = Query(..., description="Destination airport IATA code"),
    departureDate: str = Query(..., description="Departure date (YYYY-MM-DD)"),
    adults: int = Query(..., ge=1, le=9),
    returnDate: Optional[str] = Query(None, description="Return date for round trips (YYYY-MM-DD)"),
    travelClass: Optional[str] = Query(None, description="ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST"),
    max: int = Query(10, ge=1, le=250),
    currencyCode: str = Query("USD"),
    _token: str = Depends(verify_token),
):
    origin = originLocationCode.upper()
    dest = destinationLocationCode.upper()

    # Lookup route (try both directions for flexibility)
    route_data = ROUTES.get((origin, dest))

    if not route_data:
        # Return empty result — matches real Amadeus behaviour
        return {
            "meta": {"count": 0, "links": {"self": f"/v2/shopping/flight-offers?originLocationCode={origin}&destinationLocationCode={dest}&departureDate={departureDate}&adults={adults}"}},
            "data": [],
            "dictionaries": {
                "locations": {},
                "aircraft": AIRCRAFT,
                "currencies": {currencyCode: currencyCode},
                "carriers": CARRIERS,
            },
        }

    cabins = (
        [travelClass.upper()]
        if travelClass and travelClass.upper() in CABIN_MULTIPLIERS
        else list(CABIN_MULTIPLIERS.keys())
    )

    offers = []
    offer_id = 1
    seg_id = 1

    for cabin in cabins:
        base_price = route_data["basePrices"][cabin]
        for option in route_data["options"]:
            if len(offers) >= max:
                break
            offer, seg_id = _build_offer(
                offer_id=offer_id,
                segment_id_start=seg_id,
                option=option,
                dep_code=origin,
                arr_code=dest,
                dep_date=departureDate,
                cabin=cabin,
                adults=adults,
                base_price=base_price,
                return_date=returnDate,
            )
            offers.append(offer)
            offer_id += 1

        if len(offers) >= max:
            break

    # Build location dict from offers
    locations_used = {origin, dest}
    if returnDate:
        locations_used.update([origin, dest])

    return {
        "meta": {
            "count": len(offers),
            "links": {
                "self": f"/v2/shopping/flight-offers?originLocationCode={origin}&destinationLocationCode={dest}&departureDate={departureDate}&adults={adults}"
            },
        },
        "data": offers,
        "dictionaries": {
            "locations": {
                code: AIRPORTS[code]
                for code in locations_used
                if code in AIRPORTS
            },
            "aircraft": AIRCRAFT,
            "currencies": {currencyCode: currencyCode},
            "carriers": CARRIERS,
        },
    }


# ---------------------------------------------------------------------------
# POST /v1/booking/flight-orders
# ---------------------------------------------------------------------------

@router.post("/v1/booking/flight-orders", status_code=status.HTTP_201_CREATED)
def create_flight_order(
    body: dict,
    _token: str = Depends(verify_token),
):
    # Validate minimal structure
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

    order_data = body.get("data", {})
    flight_offers = order_data.get("flightOffers", [])
    travelers = order_data.get("travelers", [])

    if not flight_offers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errors": [
                    {
                        "status": 400,
                        "code": 32171,
                        "title": "MANDATORY DATA MISSING",
                        "detail": "flightOffers must not be empty",
                    }
                ]
            },
        )

    order_id = f"MOCK{uuid.uuid4().hex[:8].upper()}"

    # Build order response
    order = {
        "type": "flight-order",
        "id": order_id,
        "queuingOfficeId": "SINBA2222",
        "associatedRecords": [
            {
                "reference": f"PNR{uuid.uuid4().hex[:6].upper()}",
                "creationDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:00.000"),
                "originSystemCode": "GDS",
                "flightOfferId": fo.get("id", "1"),
            }
            for fo in flight_offers
        ],
        "flightOffers": flight_offers,
        "travelers": travelers,
        "remarks": order_data.get("remarks", {}),
        "ticketingAgreement": order_data.get("ticketingAgreement", {"option": "DELAY_TO_CANCEL", "delay": "6D"}),
        "contacts": order_data.get("contacts", []),
    }

    _flight_orders[order_id] = order

    return {"data": order}


# ---------------------------------------------------------------------------
# GET /v1/booking/flight-orders/{orderId}
# ---------------------------------------------------------------------------

@router.get("/v1/booking/flight-orders/{orderId}")
def get_flight_order(
    orderId: str,
    _token: str = Depends(verify_token),
):
    order = _flight_orders.get(orderId)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errors": [
                    {
                        "status": 404,
                        "code": 1797,
                        "title": "NOT FOUND",
                        "detail": f"Flight order '{orderId}' not found",
                    }
                ]
            },
        )
    return {"data": order}


# ---------------------------------------------------------------------------
# DELETE /v1/booking/flight-orders/{orderId}
# ---------------------------------------------------------------------------

@router.delete("/v1/booking/flight-orders/{orderId}", status_code=status.HTTP_200_OK)
def cancel_flight_order(
    orderId: str,
    _token: str = Depends(verify_token),
):
    if orderId not in _flight_orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errors": [
                    {
                        "status": 404,
                        "code": 1797,
                        "title": "NOT FOUND",
                        "detail": f"Flight order '{orderId}' not found",
                    }
                ]
            },
        )
    del _flight_orders[orderId]
    return {}
