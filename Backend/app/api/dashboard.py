from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database.connection import get_db
from app.models.zones import Zone
from app.models.alerts import Alert


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):

    zones = db.query(Zone).all()
    alerts = db.query(Alert).all()

    critical_zones = sum(
        1 for zone in zones
        if zone.risk_score >= 80
    )

    high_risk_zones = sum(
        1 for zone in zones
        if 60 <= zone.risk_score < 80
    )

    total_population = sum(
        zone.exposed_population
        for zone in zones
    )

    return {
        "critical_zones": critical_zones,
        "high_risk_zones": high_risk_zones,
        "villages_at_risk": 0,
        "road_segments_at_risk": 0,
        "active_alerts": len(alerts),
        "total_exposed_population": total_population
    }