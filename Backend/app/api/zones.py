from fastapi import APIRouter, HTTPException
import json
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database.connection import get_db
from app.models.zones import Zone
from app.services.risk_engine import calculate_risk


router = APIRouter(
    prefix="/api/zones",
    tags=["Zones"]
)


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "zones.json"


def load_zones():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@router.get("")
def get_zones():
    return {
        "count": len(load_zones()),
        "zones": load_zones()
    }


@router.get("/{zone_id}")
def get_zone(zone_id: str):

    zones = load_zones()

    for zone in zones:
        if zone["id"] == zone_id:
            return zone

    raise HTTPException(
        status_code=404,
        detail="Zone not found"
    )
@router.get("/{zone_id}/risk")
def get_zone_risk(
    zone_id: str,
    db: Session = Depends(get_db)
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    result = calculate_risk(
        rainfall_24h=zone.rainfall_24h,
        slope_degree=zone.slope_degree,
        insar_creep=zone.insar_creep
    )

    return {
        "zone_id": zone.id,
        "zone_name": zone.name,
        "location": zone.location,
        "risk": result
    }