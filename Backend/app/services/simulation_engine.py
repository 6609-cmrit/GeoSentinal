def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def simulate_scenario(
    rainfall_mm: float,
    zone_id: str,
    zone=None
):
    """
    Prototype scenario simulation.

    This is a demonstration model for the SIH prototype.
    It is NOT a scientifically validated landslide forecasting model.
    """

    if zone is None:
        raise ValueError("Zone data is required")

    # --------------------------------------------------
    # 1. Calculate rainfall intensity
    # --------------------------------------------------

    rainfall_score = clamp(
        (rainfall_mm / 150) * 100,
        0,
        100
    )

    # --------------------------------------------------
    # 2. Calculate slope contribution
    # --------------------------------------------------

    slope_score = clamp(
        (zone.slope_degree / 45) * 100,
        0,
        100
    )

    # --------------------------------------------------
    # 3. Calculate InSAR contribution
    # --------------------------------------------------

    insar_score = clamp(
        (zone.insar_creep / 5) * 100,
        0,
        100
    )

    # --------------------------------------------------
    # 4. Scenario risk
    # --------------------------------------------------

    risk = (
        rainfall_score * 0.45 +
        slope_score * 0.35 +
        insar_score * 0.20
    )

    risk = round(clamp(risk, 0, 100), 2)

    # --------------------------------------------------
    # 5. Risk tier
    # --------------------------------------------------

    if risk >= 80:
        risk_tier = "CRITICAL"
    elif risk >= 60:
        risk_tier = "HIGH"
    elif risk >= 40:
        risk_tier = "MODERATE"
    else:
        risk_tier = "LOW"

    # --------------------------------------------------
    # 6. Prototype Factor of Safety
    # --------------------------------------------------

    fos = 1.55 - (rainfall_mm / 150) * 0.75

    # Higher slope slightly reduces FoS
    fos -= max(zone.slope_degree - 25, 0) * 0.005

    fos = round(max(fos, 0.50), 2)

    if fos < 1.0:
        fos_tier = "CRITICAL"
    elif fos < 1.2:
        fos_tier = "UNSTABLE"
    elif fos < 1.5:
        fos_tier = "WATCH"
    else:
        fos_tier = "STABLE"

    # --------------------------------------------------
    # 7. Prototype pore-water pressure
    # --------------------------------------------------

    pwp_kpa = 50 + (rainfall_mm * 1.0)

    pwp_kpa = round(pwp_kpa, 2)

    # --------------------------------------------------
    # 8. Volumetric water content
    # --------------------------------------------------

    vwc_pct = clamp(
        35 + (rainfall_mm / 150) * 65,
        0,
        100
    )

    vwc_pct = round(vwc_pct, 2)

    # --------------------------------------------------
    # 9. Estimated affected population
    # --------------------------------------------------

    exposure_factor = rainfall_mm / 150

    souls = round(
        zone.exposed_population * exposure_factor
    )

    souls = max(souls, 0)

    # --------------------------------------------------
    # 10. Estimated evacuation population
    # --------------------------------------------------

    if risk >= 80:
        evac = round(souls * 0.42)
        priority = 1
    elif risk >= 60:
        evac = round(souls * 0.28)
        priority = 2
    elif risk >= 40:
        evac = round(souls * 0.12)
        priority = 3
    else:
        evac = 0
        priority = 4

    # --------------------------------------------------
    # 11. Estimated cutoff percentage
    # --------------------------------------------------

    cutoff_pct = round(
        clamp(rainfall_mm / 150 * 100, 0, 100)
    )

    if cutoff_pct >= 85:
        highway_status = "CLOSED"
    elif cutoff_pct >= 50:
        highway_status = "PARTIAL"
    else:
        highway_status = "OPEN"

    # --------------------------------------------------
    # 12. Estimated runout
    # --------------------------------------------------

    runout_radius = round(
        30 + rainfall_mm * 0.70
    )

    runout_area = round(
        3.14159 * (runout_radius / 1000) ** 2,
        2
    )

    # --------------------------------------------------
    # 13. Estimated hamlets
    # --------------------------------------------------

    hamlets = max(
        1,
        round((souls / 400))
    )

    # --------------------------------------------------
    # 14. Scenario narrative
    # --------------------------------------------------

    if risk >= 80:
        narrative = (
            f"Critical rainfall scenario for {zone.name}. "
            "Rapid escalation of slope instability is indicated "
            "by the prototype model."
        )

    elif risk >= 60:
        narrative = (
            f"High-risk rainfall scenario for {zone.name}. "
            "Slope conditions require close monitoring "
            "and preparedness planning."
        )

    elif risk >= 40:
        narrative = (
            f"Moderate-risk rainfall scenario for {zone.name}. "
            "Continued monitoring is recommended."
        )

    else:
        narrative = (
            f"Low-risk rainfall scenario for {zone.name} "
            "under the prototype model."
        )

    return {
        "zone_id": zone_id,
        "zone_name": zone.name,

        "rainfall_mm": rainfall_mm,

        "risk": risk,
        "risk_tier": risk_tier,

        "fos": fos,
        "fos_tier": fos_tier,

        "pwp_kpa": pwp_kpa,
        "vwc_pct": vwc_pct,

        "hamlets": hamlets,
        "souls": souls,
        "evac": evac,

        "cutoff_pct": cutoff_pct,
        "highway_status": highway_status,

        "priority": priority,

        "runout_radius": runout_radius,
        "runout_area": runout_area,

        "narrative": narrative
    }