"""Python calculation engine for CL1010 Smart City Simulator.

All project calculations live in this file, not in the web interface.
The functions demonstrate reusable functions, loops, conditionals, input
validation, and controlled error handling as required by the lab brief.
"""
from __future__ import annotations

import math
from typing import Any

WATER_LITRES_PER_PERSON = 135
TRAFFIC_THRESHOLDS = (25, 60, 100)  # Vehicles per kilometre
TRAFFIC_LABELS = ("Low", "Moderate", "High", "Critical")
TRAFFIC_ACTIONS = (
    "Keep normal signal timings and continue regular monitoring.",
    "Monitor peak hours, improve signal timing, and promote public transport.",
    "Activate adaptive traffic signals, deploy traffic wardens, and suggest alternate routes.",
    "Divert traffic, restrict heavy vehicles temporarily, and activate emergency congestion measures.",
)

DEMO = {
    "city_name": "Ibrahim City",
    "vehicles": 12500,
    "road_length_km": 180.0,
    "population": 250000,
    "available_water_lpd": 31000000.0,
    "building_length_m": 45.0,
    "building_width_m": 30.0,
    "floors": 8,
    "cost_per_m2": 75000.0,
    "waste_kg_per_person": 0.75,
    "recycling_percentage": 35.0,
    "population_growth_pct": 2.0,
    "vehicle_growth_pct": 3.0,
    "water_supply_growth_pct": 1.0,
    "recycling_target_pct": 60.0,
    "forecast_years": 10,
}


def _number(value: Any, name: str, *, minimum: float = 0,
            maximum: float | None = None, integer: bool = False,
            exclusive_minimum: bool = False) -> float | int:
    """Reject invalid values instead of allowing an exception to crash the app."""
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number.")
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"{name} must be a valid number.") from None
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number.")
    if value < minimum or (exclusive_minimum and value == minimum):
        op = "greater than" if exclusive_minimum else "at least"
        raise ValueError(f"{name} must be {op} {minimum:g}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be no more than {maximum:g}.")
    if integer:
        if not value.is_integer():
            raise ValueError(f"{name} must be a whole number.")
        return int(value)
    return value


def validate_city(data: dict[str, Any]) -> dict[str, Any]:
    """Return a clean validated copy of a scenario for all five modules."""
    if not isinstance(data, dict):
        raise ValueError("Scenario data must be a JSON object.")
    city_name = str(data.get("city_name", "")).strip()
    if not city_name or len(city_name) > 60:
        raise ValueError("City name must have between 1 and 60 characters.")
    clean = {"city_name": city_name}
    fields = (
        ("vehicles", "Number of vehicles", 0, 1e10, True, False),
        ("road_length_km", "Road length", 0, 1e7, False, True),
        ("population", "City population", 0, 1e10, True, True),
        ("available_water_lpd", "Available water per day", 0, 1e15, False, False),
        ("building_length_m", "Building length", 0, 1e7, False, True),
        ("building_width_m", "Building width", 0, 1e7, False, True),
        ("floors", "Number of floors", 0, 1000, True, True),
        ("cost_per_m2", "Cost per square metre", 0, 1e12, False, True),
        ("waste_kg_per_person", "Daily waste per person", 0, 100, False, True),
        ("recycling_percentage", "Recycling percentage", 0, 100, False, False),
        ("population_growth_pct", "Population growth rate", -10, 30, False, False),
        ("vehicle_growth_pct", "Vehicle growth rate", -10, 30, False, False),
        ("water_supply_growth_pct", "Water supply growth rate", -10, 30, False, False),
        ("recycling_target_pct", "Year-end recycling target", 0, 100, False, False),
        ("forecast_years", "Forecast duration", 1, 30, True, False),
    )
    # A loop keeps validation consistent across modules, instead of
    # duplicating error checks in each part of the interface.
    for key, label, minv, maxv, whole, excl in fields:
        if key not in data:
            raise ValueError(f"Missing required input: {label}.")
        clean[key] = _number(data[key], label, minimum=minv,
                             maximum=maxv, integer=whole,
                             exclusive_minimum=excl)
    return clean


def traffic_management(vehicles: int, road_length_km: float) -> dict[str, Any]:
    """Calculate vehicles/km, severity and a suitable management action."""
    vehicles = _number(vehicles, "Number of vehicles", integer=True)
    road_length_km = _number(road_length_km, "Road length", exclusive_minimum=True)
    density = vehicles / road_length_km
    if density <= TRAFFIC_THRESHOLDS[0]:
        level = 0
    elif density <= TRAFFIC_THRESHOLDS[1]:
        level = 1
    elif density <= TRAFFIC_THRESHOLDS[2]:
        level = 2
    else:
        level = 3
    return {"density": density, "condition": TRAFFIC_LABELS[level],
            "severity": level, "action": TRAFFIC_ACTIONS[level]}


def water_management(population: int, available_water_lpd: float) -> dict[str, Any]:
    """Daily demand is fixed by the teacher's rule of 135 L/person/day."""
    population = _number(population, "City population", integer=True, exclusive_minimum=True)
    available_water_lpd = _number(available_water_lpd, "Available water per day")
    demand = population * WATER_LITRES_PER_PERSON
    difference = available_water_lpd - demand
    if difference < 0:
        status = "Shortage"
    elif difference > 0:
        status = "Surplus"
    else:
        status = "Balanced"
    return {"demand_lpd": demand, "supply_lpd": available_water_lpd,
            "balance_lpd": difference, "status": status,
            "coverage_pct": 100 * available_water_lpd / demand}


def construction_estimator(length_m: float, width_m: float,
                           floors: int, cost_per_m2: float) -> dict[str, float]:
    """Assume the same footprint on every floor; display cost in PKR."""
    length_m = _number(length_m, "Building length", exclusive_minimum=True)
    width_m = _number(width_m, "Building width", exclusive_minimum=True)
    floors = _number(floors, "Number of floors", integer=True, exclusive_minimum=True)
    cost_per_m2 = _number(cost_per_m2, "Cost per square metre", exclusive_minimum=True)
    footprint = length_m * width_m
    total_floor_area = footprint * floors
    return {"footprint_m2": footprint, "total_floor_area_m2": total_floor_area,
            "total_cost_pkr": total_floor_area * cost_per_m2,
            "cost_per_floor_pkr": footprint * cost_per_m2}


def waste_management(population: int, waste_kg_per_person: float,
                     recycling_percentage: float) -> dict[str, float]:
    """Calculate generated, recycled and remaining waste in kg/day."""
    population = _number(population, "City population", integer=True, exclusive_minimum=True)
    waste_kg_per_person = _number(waste_kg_per_person, "Daily waste per person",
                                  exclusive_minimum=True)
    recycling_percentage = _number(recycling_percentage, "Recycling percentage", maximum=100)
    total = population * waste_kg_per_person
    recycled = total * recycling_percentage / 100
    return {"total_kgpd": total, "recycled_kgpd": recycled,
            "remaining_kgpd": total - recycled, "recycling_percentage": recycling_percentage}


def city_health_score(traffic: dict, water: dict, waste: dict) -> dict[str, Any]:
    """Illustrative weighted score (not a real-world government rating)."""
    traffic_score = (100, 75, 45, 15)[traffic["severity"]]
    water_score = min(100.0, water["coverage_pct"])
    recycling_score = min(100.0, waste["recycling_percentage"] * 2)
    score = 0.35 * traffic_score + 0.40 * water_score + 0.25 * recycling_score
    label = "Strong" if score >= 75 else "Developing" if score >= 50 else "Needs attention"
    return {"score": round(score, 1), "label": label,
            "traffic_score": traffic_score,
            "water_score": water_score, "recycling_score": recycling_score}


def calculate_city(data: dict[str, Any]) -> dict[str, Any]:
    """Combine four mandatory calculations into the final report dataset."""
    d = validate_city(data)
    traffic = traffic_management(d["vehicles"], d["road_length_km"])
    water = water_management(d["population"], d["available_water_lpd"])
    construction = construction_estimator(d["building_length_m"], d["building_width_m"],
                                          d["floors"], d["cost_per_m2"])
    waste = waste_management(d["population"], d["waste_kg_per_person"],
                             d["recycling_percentage"])
    health = city_health_score(traffic, water, waste)
    return {"inputs": d, "traffic": traffic, "water": water,
            "construction": construction, "waste": waste, "health": health,
            "recommendations": recommendations(traffic, water, waste)}


def recommendations(traffic: dict, water: dict, waste: dict) -> list[str]:
    """Use conditions to create a final city-wide management summary."""
    output = [f"TRAFFIC: {traffic['action']}"]
    if water["balance_lpd"] < 0:
        output.append(f"WATER: Increase daily supply or conserve {abs(water['balance_lpd']):,.0f} litres.")
    elif water["balance_lpd"] > 0:
        output.append("WATER: Supply exceeds today's demand. Monitor reserve capacity.")
    else:
        output.append("WATER: Supply exactly meets demand. Build an emergency reserve.")
    if waste["recycling_percentage"] < 30:
        output.append("WASTE: Low recycling rate. Expand segregation bins and community outreach.")
    elif waste["recycling_percentage"] < 60:
        output.append("WASTE: Increase recycling coverage and improve collection routes.")
    else:
        output.append("WASTE: Maintain and audit the strong recycling programme.")
    return output


def forecast_city(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Model an illustrative future using annual compound growth assumptions."""
    d = validate_city(data)
    years = d["forecast_years"]
    rows = []
    # Loop over years; every record can be plotted or added to the PDF report.
    for year in range(years + 1):
        population = d["population"] * (1 + d["population_growth_pct"] / 100) ** year
        vehicles = d["vehicles"] * (1 + d["vehicle_growth_pct"] / 100) ** year
        supply = d["available_water_lpd"] * (1 + d["water_supply_growth_pct"] / 100) ** year
        demand = population * WATER_LITRES_PER_PERSON
        waste = population * d["waste_kg_per_person"]
        recycle_pct = d["recycling_percentage"] + (
            d["recycling_target_pct"] - d["recycling_percentage"]
        ) * year / years
        density = vehicles / d["road_length_km"]
        rows.append({"year": year, "population": round(population),
                     "vehicles": round(vehicles), "traffic_density": density,
                     "water_demand_lpd": demand, "water_supply_lpd": supply,
                     "water_balance_lpd": supply - demand,
                     "waste_tonnes_pd": waste / 1000,
                     "recycled_tonnes_pd": waste * recycle_pct / 100 / 1000,
                     "recycling_pct": recycle_pct})
    return rows


def forecast_alerts(rows: list[dict[str, Any]]) -> list[str]:
    """Identify thresholds reached within the chosen forecast horizon."""
    alerts = []
    first_shortage = next((r for r in rows if r["water_balance_lpd"] < 0), None)
    first_critical = next((r for r in rows if r["traffic_density"] > 100), None)
    alerts.append(
        f"Water shortages {'begin' if first_shortage['year'] else 'already exist'} in year {first_shortage['year']}."
        if first_shortage is not None else "Water supply covers projected demand throughout the forecast."
    )
    alerts.append(
        f"Critical traffic {'begins' if first_critical['year'] else 'already exists'} in year {first_critical['year']}."
        if first_critical is not None else "Traffic density stays below the critical threshold throughout the forecast."
    )
    return alerts
