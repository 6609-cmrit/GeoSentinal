from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.scenario import ScenarioRequest
from app.services.simulation_engine import simulate_scenario
from app.database.connection import get_db
from app.models.zones import Zone


router = APIRouter(
    prefix="/api/scenarios",
    tags=["Scenarios"]
)


@router.post("/simulate")
def run_simulation(
    request: ScenarioRequest,
    db: Session = Depends(get_db)
):

    # Find the selected zone
    zone = db.query(Zone).filter(
        Zone.id == request.zone_id
    ).first()

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    # Run scenario using the selected zone
    result = simulate_scenario(
        rainfall_mm=request.rainfall_mm,
        zone_id=request.zone_id,
        zone=zone
    )

    return result