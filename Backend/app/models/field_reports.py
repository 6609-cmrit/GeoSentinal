from sqlalchemy import Column, Integer, String, Text
from app.database.connection import Base


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(Integer, primary_key=True, index=True)

    zone_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    type = Column(String, nullable=False)

    location = Column(String, nullable=False)
    notes = Column(Text, nullable=False)
    reporter = Column(String, nullable=False)