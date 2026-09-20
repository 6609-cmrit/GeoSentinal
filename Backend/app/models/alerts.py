from sqlalchemy import Column, Integer, String, Text
from app.database.connection import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    zone_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    channels = Column(String, nullable=False)