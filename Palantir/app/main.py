import os
import calendar
from datetime import date
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from app.core.config import settings
import foundry_rest_api_sdk
from foundry_rest_api_sdk.ontology.search._example_flight_object_type import ExampleFlightObjectType as FT
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Foundry REST API")

FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (fine for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client():
    return foundry_rest_api_sdk.FoundryClient(
        auth=foundry_rest_api_sdk.UserTokenAuth(token=settings.FOUNDRY_TOKEN),
        hostname=settings.FOUNDRY_HOSTNAME,
    )

@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_PATH)

@app.get("/health")
def health():
    return {"status": "ok", "host": settings.FOUNDRY_HOSTNAME}


@app.get("/airports")
def list_airports():
    try:
        client = get_client()
        ontology = client.ontology
        airports = []
        for airport in ontology.objects.ExampleAirport.iterate():
            airports.append({
                "name": airport.display_airport_name,
                "code": airport.airport,
                "city": airport.display_airport_city_name_full,
                "state": airport.airport_state_name,
                "lat": airport.latitude,
                "lng": airport.longitude,
                "avg_dep_delay": round(airport.average_dep_delay or 0, 2),
                "avg_arr_delay": round(airport.average_arr_delay or 0, 2),
            })
        return {"total": len(airports), "airports": airports}
    except Exception as e:
        return {"error": str(e)}

@app.get("/delays")
def get_delays(month: int = Query(None, ge=1, le=12)):
    try:
        client = get_client()
        F = client.ontology.objects.ExampleFlight

        if month is None:
            filtered = F
        else:
            last_day = calendar.monthrange(2023, month)[1]
            start = date(2023, month, 1)
            end = date(2023, month, last_day)
            filtered = F.where((FT.date_ >= start) & (FT.date_ <= end))

        result = (
            filtered
            .group_by(FT.origin_airport.exact())
            .aggregate({
                "avg_dep_delay": FT.dep_delay.avg(),
                "avg_arr_delay": FT.arr_delay.avg(),
            })
            .compute()
        )

        delays = {}
        for item in result.data:
            code = item.group.get("originAirport")
            if not code:
                continue
            metrics = {m.name: m.value for m in item.metrics}
            delays[str(code)] = {
                "avg_dep_delay": round(float(metrics.get("avg_dep_delay") or 0), 2),
                "avg_arr_delay": round(float(metrics.get("avg_arr_delay") or 0), 2),
            }

        return {"month": month, "delays": delays}
    except Exception as e:
        return {"error": str(e)}

@app.get("/routes/{airport_code}")
def get_routes_for_airport(airport_code: str):
    try:
        client = get_client()
        code = airport_code.upper()
        F = client.ontology.objects.ExampleFlight

        result = (
            F.where(FT.origin_airport == code)
            .group_by(FT.destination_airport.exact())
            .aggregate({
                "avg_dep_delay": FT.dep_delay.avg(),
                "avg_arr_delay": FT.arr_delay.avg(),
            })
            .compute()
        )

        routes = []
        for item in result.data:
            dest = item.group.get("destinationAirport")
            if not dest:
                continue
            metrics = {m.name: m.value for m in item.metrics}
            routes.append({
                "destination": str(dest),
                "avg_dep_delay": round(float(metrics.get("avg_dep_delay") or 0), 2),
                "avg_arr_delay": round(float(metrics.get("avg_arr_delay") or 0), 2),
            })

        return {"airport": code, "total": len(routes), "routes": routes}
    except Exception as e:
        return {"error": str(e)}
