from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.alerts import router as alerts_router
from app.api.scenarios import router as scenarios_router
from app.database.connection import Base, engine

from app.models.alerts import Alert
from app.models.field_reports import FieldReport
from app.models.zones import Zone

from app.api.field_reports import router as field_reports_router
from app.api.zones import router as zones_router
from app.api.dashboard import router as dashboard_router
from app.api.locations import router as locations_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GeoSentinel API",
    description="Landslide Early Warning and Spatial Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "GeoSentinel Backend is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(field_reports_router)
app.include_router(alerts_router)
app.include_router(scenarios_router)
app.include_router(zones_router)
app.include_router(dashboard_router)
app.include_router(locations_router)
