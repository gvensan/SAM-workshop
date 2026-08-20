from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, flights, hotels

app = FastAPI(
    title="Amadeus Travel API Mock",
    description=(
        "Mock implementation of the Amadeus Self-Service APIs.\n\n"
        "**Default credentials:** `client_id=test` / `client_secret=test`\n\n"
        "Set `REQUIRE_AUTH=false` to skip token validation entirely."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
app.include_router(auth.router, prefix="/v1/security")

# Flights
app.include_router(flights.router)

# Hotels
app.include_router(hotels.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "amadeus-mock", "version": "1.0.0"}


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Amadeus Travel API Mock",
        "docs": "/docs",
        "endpoints": [
            "POST /v1/security/oauth2/token",
            "GET  /v2/shopping/flight-offers",
            "POST /v1/booking/flight-orders",
            "GET  /v1/booking/flight-orders/{orderId}",
            "DELETE /v1/booking/flight-orders/{orderId}",
            "GET  /v1/reference-data/locations/hotels/by-city",
            "GET  /v3/shopping/hotel-offers",
            "GET  /v3/shopping/hotel-offers/{offerId}",
            "POST /v2/booking/hotel-orders",
            "GET  /v2/booking/hotel-orders/{orderId}",
        ],
    }
