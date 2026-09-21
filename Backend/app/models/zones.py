from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.zones import Zone
from app.services.risk_engine import calculate_risk
from app.services.weather_service import get_last_24h_rainfall


router = APIRouter(
    prefix="/api/zones",
    tags=["Zones"]
)


@router.get("")
def get_zones(
    db: Session = Depends(get_db)
):
    """
    Return all monitored zones with dynamically
    updated weather/risk information.
    """

    zones = db.query(Zone).all()

    result = []

    for zone in zones:

        weather_error = None

        try:
            weather = get_last_24h_rainfall(
                latitude=zone.latitude,
                longitude=zone.longitude
            )

            rainfall_24h = weather["rainfall_24h"]

            # Update database rainfall value
            zone.rainfall_24h = rainfall_24h

        except Exception as error:

            # Keep existing stored value if weather API fails
            rainfall_24h = zone.rainfall_24h
            weather_error = str(error)

        # Recalculate risk using current rainfall
        risk = calculate_risk(
            rainfall_24h=rainfall_24h,
            slope_degree=zone.slope_degree,
            insar_creep=zone.insar_creep
        )

        # Update stored risk values
        zone.risk_score = risk["risk_score"]
        zone.risk_level = risk["risk_tier"]

        result.append({
            "id": zone.id,
            "name": zone.name,
            "location": zone.location,
            "latitude": zone.latitude,
            "longitude": zone.longitude,

            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_tier"],

            "ai_confidence": zone.ai_confidence,

            "rainfall_24h": rainfall_24h,
            "slope_degree": zone.slope_degree,
            "insar_creep": zone.insar_creep,

            "exposed_population": zone.exposed_population,

            "weather_source": "Open-Meteo"
                if weather_error is None
                else "Stored value",

            "weather_error": weather_error
        })

    db.commit()

    return {
        "count": len(result),
        "zones": result
    }


@router.get("/{zone_id}")
def get_zone(
    zone_id: str,
    db: Session = Depends(get_db)
):
    """
    Return a single zone with dynamically updated
    weather and risk information.
    """

    zone = (
        db.query(Zone)
        .filter(Zone.id == zone_id)
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    weather_error = None

    try:
        weather = get_last_24h_rainfall(
            latitude=zone.latitude,
            longitude=zone.longitude
        )

        rainfall_24h = weather["rainfall_24h"]

        zone.rainfall_24h = rainfall_24h

    except Exception as error:

        rainfall_24h = zone.rainfall_24h
        weather_error = str(error)

    risk = calculate_risk(
        rainfall_24h=rainfall_24h,
        slope_degree=zone.slope_degree,
        insar_creep=zone.insar_creep
    )

    zone.risk_score = risk["risk_score"]
    zone.risk_level = risk["risk_tier"]

    db.commit()

    return {
        "id": zone.id,
        "name": zone.name,
        "location": zone.location,

        "latitude": zone.latitude,
        "longitude": zone.longitude,

        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_tier"],

        "ai_confidence": zone.ai_confidence,

        "rainfall_24h": rainfall_24h,
        "slope_degree": zone.slope_degree,
        "insar_creep": zone.insar_creep,

        "exposed_population": zone.exposed_population,

        "weather_source": "Open-Meteo"
            if weather_error is None
            else "Stored value",

        "weather_error": weather_error
    }


@router.get("/{zone_id}/risk")
def get_zone_risk(
    zone_id: str,
    db: Session = Depends(get_db)
):
    """
    Calculate current zone risk using dynamically
    retrieved rainfall data.
    """

    zone = (
        db.query(Zone)
        .filter(Zone.id == zone_id)
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    weather_error = None

    try:

        weather = get_last_24h_rainfall(
            latitude=zone.latitude,
            longitude=zone.longitude
        )

        rainfall_24h = weather["rainfall_24h"]

        zone.rainfall_24h = rainfall_24h

    except Exception as error:

        rainfall_24h = zone.rainfall_24h
        weather_error = str(error)

    result = calculate_risk(
        rainfall_24h=rainfall_24h,
        slope_degree=zone.slope_degree,
        insar_creep=zone.insar_creep
    )

    zone.risk_score = result["risk_score"]
    zone.risk_level = result["risk_tier"]

    db.commit()

    return {
        "zone_id": zone.id,
        "zone_name": zone.name,
        "location": zone.location,

        "rainfall_24h": rainfall_24h,

        "risk": result,

        "weather_source": "Open-Meteo"
            if weather_error is None
            else "Stored value",

        "weather_error": weather_error
    }