"""Downloadable, professionally formatted PDF report for the Smart City app."""
from __future__ import annotations

from datetime import datetime
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

NAVY = colors.HexColor("#22223B")
SLATE = colors.HexColor("#4A4E69")
MAUVE = colors.HexColor("#9A8C98")
ROSE = colors.HexColor("#C9ADA7")
CREAM = colors.HexColor("#F2E9E4")


def _fmt(v: float, decimals: int = 0) -> str:
    return f"{v:,.{decimals}f}"


def create_pdf_report(result: dict, forecast: list[dict]) -> bytes:
    """Generate a two-to-three-page PDF from validated Python calculations."""
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=1.65*cm,
                            leftMargin=1.65*cm, topMargin=1.8*cm,
                            bottomMargin=1.6*cm, title="Smart City Analysis Report")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DocTitleCustom", fontName="Helvetica-Bold", fontSize=21,
                              leading=26, textColor=NAVY, spaceAfter=6))
    styles.add(ParagraphStyle(name="DocSubtitleCustom", fontName="Helvetica", fontSize=9,
                              leading=14, textColor=SLATE, spaceAfter=13))
    styles.add(ParagraphStyle(name="DocHeadingCustom", fontName="Helvetica-Bold", fontSize=12,
                              textColor=NAVY, leading=16, spaceBefore=13, spaceAfter=7))
    styles.add(ParagraphStyle(name="DocBodyCustom", fontName="Helvetica", fontSize=9,
                              textColor=NAVY, leading=14, spaceAfter=5))
    styles.add(ParagraphStyle(name="DocSmallCustom", fontName="Helvetica", fontSize=8,
                              textColor=SLATE, leading=11, spaceAfter=4))
    styles.add(ParagraphStyle(name="DocItemCustom", fontName="Helvetica", fontSize=8.8,
                              textColor=NAVY, leading=14, leftIndent=10, firstLineIndent=-10, spaceAfter=6))

    story = []
    d, traffic, water = result["inputs"], result["traffic"], result["water"]
    build, waste, health = result["construction"], result["waste"], result["health"]
    story.append(Paragraph("SMART CITY | ANALYSIS REPORT", styles["DocTitleCustom"]))
    story.append(Paragraph(f"{escape(d['city_name'])}  |  Generated {datetime.now():%d %B %Y}  |  CP Lab CL1010", styles["DocSubtitleCustom"]))
    story.append(Paragraph(f"City health index: <b>{health['score']:.1f}/100</b>  ({escape(health['label'])})",
                           styles["DocBodyCustom"]))
    story.append(Paragraph("The health index is an illustrative classroom planning score, not an official city rating.",
                           styles["DocSmallCustom"]))

    def section(title: str, data: list[tuple[str, str]]) -> None:
        story.append(Paragraph(title, styles["DocHeadingCustom"]))
        rows = [[Paragraph(escape(str(k)), styles["DocBodyCustom"]),
                 Paragraph(escape(str(v)), styles["DocBodyCustom"])] for k, v in data]
        table = Table(rows, colWidths=[7.4*cm, 9.2*cm], hAlign="LEFT")
        table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, colors.white]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, -1), (-1, -1), .5, ROSE),
        ]))
        story.append(table)

    section("01  /  TRAFFIC MANAGEMENT", [
        ("Vehicles passing through road", _fmt(d["vehicles"])),
        ("Road length", f"{_fmt(d['road_length_km'], 2)} km"),
        ("Traffic density", f"{_fmt(traffic['density'], 2)} vehicles/km"),
        ("Traffic condition", traffic["condition"]),
    ])
    story.append(Paragraph(f"Recommended action: {escape(traffic['action'])}", styles["DocSmallCustom"]))
    section("02  /  WATER SUPPLY", [
        ("City population", _fmt(d["population"])),
        ("Daily water demand", f"{_fmt(water['demand_lpd'])} litres/day"),
        ("Available water supply", f"{_fmt(water['supply_lpd'])} litres/day"),
        ("Water condition", f"{water['status']} ({_fmt(abs(water['balance_lpd']))} litres/day)"),
    ])
    section("03  /  CONSTRUCTION COST ESTIMATOR", [
        ("Building dimensions", f"{_fmt(d['building_length_m'], 1)} m x {_fmt(d['building_width_m'], 1)} m"),
        ("Floors", _fmt(d["floors"])),
        ("Total floor area", f"{_fmt(build['total_floor_area_m2'], 2)} m2"),
        ("Rate", f"PKR {_fmt(d['cost_per_m2'], 2)} /m2"),
        ("Estimated total budget", f"PKR {_fmt(build['total_cost_pkr'], 2)}"),
    ])
    section("04  /  WASTE MANAGEMENT", [
        ("Daily waste per person", f"{_fmt(d['waste_kg_per_person'], 2)} kg"),
        ("Total daily waste", f"{_fmt(waste['total_kgpd'], 2)} kg"),
        ("Recycling target", f"{_fmt(d['recycling_percentage'], 1)}%"),
        ("Daily waste to recycle", f"{_fmt(waste['recycled_kgpd'], 2)} kg"),
        ("Waste for disposal", f"{_fmt(waste['remaining_kgpd'], 2)} kg"),
    ])
    story.append(PageBreak())
    story.append(Paragraph("05  /  EXECUTIVE RECOMMENDATIONS", styles["DocHeadingCustom"]))
    for recommendation in result["recommendations"]:
        story.append(Paragraph(f"- {escape(recommendation)}", styles["DocItemCustom"]))

    story.append(Paragraph("06  /  FORECAST SNAPSHOT", styles["DocHeadingCustom"]))
    ends = forecast[-1]
    section("Future planning (illustrative)", [
        ("Forecast horizon", f"{ends['year']} years"),
        ("Projected population", _fmt(ends["population"])),
        ("Projected traffic density", f"{_fmt(ends['traffic_density'], 1)} vehicles/km"),
        ("Projected water balance", f"{_fmt(ends['water_balance_lpd'])} litres/day"),
        ("Projected daily recycled waste", f"{_fmt(ends['recycled_tonnes_pd'], 1)} tonnes/day"),
    ])
    story.append(Paragraph("YEAR-BY-YEAR OUTLOOK", styles["DocHeadingCustom"]))
    columns = ["Year", "People", "Traffic/km", "Water demand (M L)", "Supply (M L)", "Recycled (t)"]
    samples = forecast if len(forecast) <= 11 else [forecast[0], *forecast[1:-1:max(1, (len(forecast)-2)//9)], forecast[-1]]
    lines = [columns]
    for r in samples:
        lines.append([str(r["year"]), _fmt(r["population"]),
                      _fmt(r["traffic_density"], 1),
                      _fmt(r["water_demand_lpd"] / 1e6, 2),
                      _fmt(r["water_supply_lpd"] / 1e6, 2),
                      _fmt(r["recycled_tonnes_pd"], 1)])
    grid = Table(lines, colWidths=[1.35*cm, 2.5*cm, 2.35*cm, 3.55*cm, 3.45*cm, 3.4*cm], repeatRows=1)
    grid.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CREAM, colors.white]),
        ("FONTSIZE", (0,0), (-1,-1), 7.6),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ALIGN", (0,0), (-1,-1), "RIGHT"),
    ]))
    story.append(grid)
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "ASSUMPTIONS: Density is vehicles divided by road length. Traffic thresholds are "
        "Low: up to 25; Moderate: above 25 to 60; High: above 60 to 100; Critical: above 100 vehicles/km. "
        "Water use is fixed at 135 L/person/day. Construction assumes an identical footprint on each floor. "
        "Future projections are mathematical scenarios, not real sensor measurements or official forecasts.",
        styles["DocSmallCustom"],
    ))

    def footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(ROSE)
        canvas.line(1.65 * cm, 1.25 * cm, w - 1.65 * cm, 1.25 * cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(SLATE)
        canvas.drawString(1.65 * cm, .9 * cm, "CL1010 | Python Smart City Simulator")
        canvas.drawRightString(w - 1.65 * cm, .9 * cm, f"Page {doc.page}")
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return stream.getvalue()
