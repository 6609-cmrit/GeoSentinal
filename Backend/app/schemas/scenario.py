from pydantic import BaseModel


class ScenarioRequest(BaseModel):
    rainfall_mm: float
    zone_id: str