from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.field_report import FieldReportCreate
from app.models.field_reports import FieldReport
from app.database.connection import get_db


router = APIRouter(
    prefix="/api/field-reports",
    tags=["Field Reports"]
)

@router.get("")
def get_field_reports(db: Session = Depends(get_db)):
    reports = db.query(FieldReport).order_by(FieldReport.id.desc()).all()

    return {
        "count": len(reports),
        "reports": [
            {
                "id": report.id,
                "zone_id": report.zone_id,
                "severity": report.severity,
                "type": report.type,
                "location": report.location,
                "notes": report.notes,
                "reporter": report.reporter
            }
            for report in reports
        ]
    }


@router.post("")
def create_field_report(
    report: FieldReportCreate,
    db: Session = Depends(get_db)
):
    new_report = FieldReport(
        zone_id=report.zone_id,
        severity=report.severity,
        type=report.type,
        location=report.location,
        notes=report.notes,
        reporter=report.reporter
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Field report submitted successfully",
        "report": {
            "id": new_report.id,
            "zone_id": new_report.zone_id,
            "severity": new_report.severity,
            "type": new_report.type,
            "location": new_report.location,
            "notes": new_report.notes,
            "reporter": new_report.reporter
        }
    }