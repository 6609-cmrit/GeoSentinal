from pydantic import BaseModel
from typing import List


class AlertCreate(BaseModel):
    zone_id: str
    severity: str
    title: str
    message: str
    channels: List[str]