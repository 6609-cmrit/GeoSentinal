from pydantic import BaseModel


class FieldReportCreate(BaseModel):
    zone_id: str
    severity: str
    type: str
    location: str
    notes: str
    reporter: str
    