from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

import json
from pathlib import Path

from app.database.connection import get_db
from app.models.zones import Zone


router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"]
)


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "locations.json"


# ---------------------------------------------------------
# Prototype mapping between monitored zones and districts
# ---------------------------------------------------------
# This does NOT mean the entire district is monitored.
# It only identifies which administrative district contains
# the currently configured GeoSentinel monitoring zones.

MONITORED_LOCATION_ZONE_MAP = {
    "nagaland-kohima": [
        "zone-a",
        "zone-b"
    ],
    "nagaland-chumoukedima": [
        "zone-c"
    ]
}


# ---------------------------------------------------------
# Load administrative location data
# ---------------------------------------------------------

def load_location_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# Convert state/district structure into flat locations
# ---------------------------------------------------------

def build_flat_locations(data):
    locations = []

    for state in data.get("states", []):
        for district in state.get("districts", []):

            location_id = (
                f"{state['id']}-"
                f"{district.lower().replace(' ', '-').replace('.', '')}"
            )

            locations.append({
                "id": location_id,
                "name": district,
                "state": state["name"],
                "state_id": state["id"],
                "type": "district"
            })

    return locations


# ---------------------------------------------------------
# GET all locations
# ---------------------------------------------------------

@router.get("")
def get_locations():
    """
    Return all administrative states and districts.
    """

    data = load_location_data()
    locations = build_flat_locations(data)

    return {
        "state_count": len(data.get("states", [])),
        "district_count": len(locations),
        "states": data.get("states", []),
        "locations": locations
    }


# ---------------------------------------------------------
# SEARCH LOCATIONS
# ---------------------------------------------------------

@router.get("/search")
def search_locations(
    q: str = Query(..., min_length=1)
):
    """
    Search districts or states by name.
    """

    data = load_location_data()
    locations = build_flat_locations(data)

    query = q.strip().lower()

    results = [
        location
        for location in locations
        if (
            query in location["name"].lower()
            or query in location["state"].lower()
        )
    ]

    return {
        "query": q,
        "count": len(results),
        "results": results
    }


# ---------------------------------------------------------
# COVERAGE ENDPOINT
# ---------------------------------------------------------

@router.get("/coverage")
def get_location_coverage(
    db: Session = Depends(get_db)
):
    """
    Return administrative coverage together with
    currently monitored GeoSentinel zones.

    REGIONAL_COVERAGE:
        Administrative location exists in GeoSentinel
        coverage data but does not currently have a
        configured monitoring zone.

    MONITORED:
        At least one GeoSentinel monitoring zone is
        currently associated with the location.
    """

    data = load_location_data()

    # Get all currently configured monitoring zones
    zones = db.query(Zone).all()

    # Create quick lookup by zone ID
    zone_lookup = {
        zone.id: zone
        for zone in zones
    }

    states = []

    monitored_district_count = 0
    monitored_zone_count = 0

    for state in data.get("states", []):

        state_result = {
            "id": state["id"],
            "name": state["name"],
            "districts": []
        }

        for district in state.get("districts", []):

            location_id = (
                f"{state['id']}-"
                f"{district.lower().replace(' ', '-').replace('.', '')}"
            )

            configured_zone_ids = MONITORED_LOCATION_ZONE_MAP.get(
                location_id,
                []
            )

            # Only include zones that actually exist in database
            valid_zone_ids = [
                zone_id
                for zone_id in configured_zone_ids
                if zone_id in zone_lookup
            ]

            monitoring_status = (
                "MONITORED"
                if valid_zone_ids
                else "REGIONAL_COVERAGE"
            )

            if valid_zone_ids:
                monitored_district_count += 1
                monitored_zone_count += len(valid_zone_ids)

            state_result["districts"].append({
                "id": location_id,
                "name": district,
                "state": state["name"],
                "state_id": state["id"],
                "type": "district",
                "monitoring_status": monitoring_status,
                "zone_count": len(valid_zone_ids),
                "zone_ids": valid_zone_ids
            })

        states.append(state_result)

    return {
        "state_count": len(states),
        "district_count": sum(
            len(state["districts"])
            for state in states
        ),
        "monitored_district_count": monitored_district_count,
        "monitored_zone_count": monitored_zone_count,
        "coverage_model": {
            "MONITORED": "District currently has one or more configured GeoSentinel monitoring zones.",
            "REGIONAL_COVERAGE": "District is included in administrative coverage but has no configured monitoring zone yet."
        },
        "states": states
    }

# ---------------------------------------------------------
# LOCATION-SPECIFIC MONITORING
# ---------------------------------------------------------

@router.get("/{location_id}/monitoring")
def get_location_monitoring(
    location_id: str,
    db: Session = Depends(get_db)
):
    """
    Return monitoring information for a specific
    administrative district.

    A district can have either:

    MONITORED
        One or more active GeoSentinel monitoring zones.

    REGIONAL_COVERAGE
        Administrative coverage exists, but no
        monitoring zone is currently configured.
    """

    data = load_location_data()
    locations = build_flat_locations(data)

    # Find requested administrative location
    selected_location = None

    for location in locations:
        if location["id"] == location_id:
            selected_location = location
            break

    if selected_location is None:
        raise HTTPException(
            status_code=404,
            detail="Location not found"
        )

    # Get configured zone IDs for this location
    configured_zone_ids = MONITORED_LOCATION_ZONE_MAP.get(
        location_id,
        []
    )

    # Fetch all zones once
    zones = db.query(Zone).all()

    zone_lookup = {
        zone.id: zone
        for zone in zones
    }

    # Only return zones that actually exist
    monitored_zones = []

    for zone_id in configured_zone_ids:

        zone = zone_lookup.get(zone_id)

        if zone is None:
            continue

        monitored_zones.append({
            "id": zone.id,
            "name": zone.name,
            "location": zone.location,
            "latitude": zone.latitude,
            "longitude": zone.longitude,
            "risk_score": zone.risk_score,
            "risk_level": zone.risk_level,
            "ai_confidence": zone.ai_confidence,
            "rainfall_24h": zone.rainfall_24h,
            "slope_degree": zone.slope_degree,
            "insar_creep": zone.insar_creep,
            "exposed_population": zone.exposed_population
        })

    monitoring_status = (
        "MONITORED"
        if monitored_zones
        else "REGIONAL_COVERAGE"
    )

    return {
        "location_id": selected_location["id"],
        "location_name": selected_location["name"],
        "state": selected_location["state"],
        "state_id": selected_location["state_id"],
        "monitoring_status": monitoring_status,
        "zone_count": len(monitored_zones),
        "zones": monitored_zones
    }


# ---------------------------------------------------------
# GET SINGLE LOCATION
# ---------------------------------------------------------

@router.get("/{location_id}")
def get_location(
    location_id: str
):
    """
    Return a single administrative location.
    """

    data = load_location_data()
    locations = build_flat_locations(data)

    for location in locations:
        if location["id"] == location_id:
            return location

    raise HTTPException(
        status_code=404,
        detail="Location not found"
    )