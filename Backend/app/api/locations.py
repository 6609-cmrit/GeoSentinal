from fastapi import APIRouter, HTTPException, Query
import json
from pathlib import Path

router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "locations.json"


def load_location_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_flat_locations(data):
    locations = []

    for state in data.get("states", []):
        for district in state.get("districts", []):
            locations.append({
                "id": f"{state['id']}-{district.lower().replace(' ', '-').replace('.', '')}",
                "name": district,
                "state": state["name"],
                "state_id": state["id"],
                "type": "district"
            })

    return locations


@router.get("")
def get_locations():
    data = load_location_data()
    locations = build_flat_locations(data)

    return {
        "state_count": len(data.get("states", [])),
        "district_count": len(locations),
        "states": data.get("states", []),
        "locations": locations
    }


@router.get("/search")
def search_locations(
    q: str = Query(..., min_length=1)
):
    data = load_location_data()
    locations = build_flat_locations(data)

    query = q.strip().lower()

    results = [
        location
        for location in locations
        if query in location["name"].lower()
        or query in location["state"].lower()
    ]

    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/{location_id}")
def get_location(location_id: str):
    data = load_location_data()
    locations = build_flat_locations(data)

    for location in locations:
        if location["id"] == location_id:
            return location

    raise HTTPException(
        status_code=404,
        detail="Location not found"
    )