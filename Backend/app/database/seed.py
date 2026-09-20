import json
from pathlib import Path

from app.database.connection import SessionLocal
from app.models.zones import Zone


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "zones.json"


def seed_zones():

    db = SessionLocal()

    try:
        existing_zones = db.query(Zone).count()

        if existing_zones > 0:
            print("Zones already exist. Skipping seed.")
            return

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            zones = json.load(file)

        for zone_data in zones:

            zone = Zone(
                id=zone_data["id"],
                name=zone_data["name"],
                location=zone_data["location"],
                latitude=zone_data["latitude"],
                longitude=zone_data["longitude"],
                risk_score=zone_data["risk_score"],
                risk_level=zone_data["risk_level"],
                ai_confidence=zone_data["ai_confidence"],
                rainfall_24h=zone_data["rainfall_24h"],
                slope_degree=zone_data["slope_degree"],
                insar_creep=zone_data["insar_creep"],
                exposed_population=zone_data["exposed_population"]
            )

            db.add(zone)

        db.commit()

        print(f"Successfully seeded {len(zones)} zones.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_zones()