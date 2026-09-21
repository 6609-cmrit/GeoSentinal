from sqlalchemy import Column, Float, Integer, String

from app.database.connection import Base


class Zone(Base):
    """A monitored location and its current landslide-risk inputs."""

    __tablename__ = "zones"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    ai_confidence = Column(Float, nullable=False)

    rainfall_24h = Column(Float, nullable=False)
    slope_degree = Column(Float, nullable=False)
    insar_creep = Column(Float, nullable=False)

    exposed_population = Column(Integer, nullable=False)
