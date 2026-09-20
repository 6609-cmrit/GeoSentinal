def calculate_risk(
    rainfall_24h: float,
    slope_degree: float,
    insar_creep: float
):
    """
    Prototype risk calculation for GeoSentinel.

    This is a transparent prototype formula.
    It is NOT a scientifically validated landslide prediction model.
    """

    # Normalize rainfall
    rainfall_score = min((rainfall_24h / 150) * 100, 100)

    # Normalize slope
    slope_score = min((slope_degree / 45) * 100, 100)

    # Normalize InSAR creep
    insar_score = min((insar_creep / 5) * 100, 100)

    # Weighted risk score
    risk_score = (
        rainfall_score * 0.45 +
        slope_score * 0.35 +
        insar_score * 0.20
    )

    risk_score = round(min(max(risk_score, 0), 100), 2)

    # Risk tier
    if risk_score >= 80:
        risk_tier = "CRITICAL"
    elif risk_score >= 60:
        risk_tier = "HIGH"
    elif risk_score >= 40:
        risk_tier = "MODERATE"
    else:
        risk_tier = "LOW"

    return {
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "components": {
            "rainfall_score": round(rainfall_score, 2),
            "slope_score": round(slope_score, 2),
            "insar_score": round(insar_score, 2)
        }
    }