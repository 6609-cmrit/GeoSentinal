from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.schemas.alerts import AlertCreate
from app.models.alerts import Alert
from app.database.connection import get_db


router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)

@router.get("")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.id.desc()).all()

    return {
        "count": len(alerts),
        "alerts": [
            {
                "id": alert.id,
                "zone_id": alert.zone_id,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "channels": alert.channels.split(",")
            }
            for alert in alerts
        ]
    }

@router.post("")
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    # Generate public alert ID
    alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

    # Create database record
    new_alert = Alert(
        zone_id=alert.zone_id,
        severity=alert.severity,
        title=alert.title,
        message=alert.message,
        channels=",".join(alert.channels)
    )

    # Save alert to SQLite
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    # Return response
    return {
        "message": "Alert created successfully",
        "alert": {
            "id": alert_id,
            "database_id": new_alert.id,
            "zone_id": new_alert.zone_id,
            "severity": new_alert.severity,
            "title": new_alert.title,
            "message": new_alert.message,
            "channels": alert.channels
        }
    }