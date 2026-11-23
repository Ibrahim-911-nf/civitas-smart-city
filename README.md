# CIVITAS — Smart City Simulator

**CP Lab CL1010 | Computer Programming Lab | Python Application**

A fully functional Python-driven city simulator, based directly on the teacher's Smart City Simulator brief. Design palette: `#22223B`, `#4A4E69`, `#9A8C98`, `#C9ADA7`, `#F2E9E4`.

## Launch the application

Install **Python 3.10 or later** from [python.org](https://www.python.org/downloads/) if needed.

**Windows (Command Prompt or VS Code terminal)**

```cmd
cd Ibrahim_Smart_City_Simulator
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If `python` is not recognized, try `py` instead:

```cmd
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

**macOS / Linux**

```bash
cd Ibrahim_Smart_City_Simulator
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

The app opens in your browser at the local URL shown in the terminal (normally **http://localhost:8501**). It runs locally; no account, Firebase, API key or internet connection is needed *after* dependencies have been installed. Font loading from Google Fonts is optional; the system font is used when offline.

## Modules required by the teacher

| Module | Required inputs | Python calculation/output |
|---|---|---|
| 1. Traffic | Number of vehicles; road length | Vehicles/km, Low/Moderate/High/Critical, suggested action |
| 2. Water | Population; available daily water supply | Daily demand at 135 L/person, shortage/surplus |
| 3. Construction | Length, width, floors, cost/m² | Floor area and estimated PKR construction budget |
| 4. Waste | Population, waste generated per person, recycling % | Total waste, recyclable portion, remaining waste |
| 5. Final report | Combined earlier module inputs | Summary, recommendations, PDF/text downloads |

### Additional features

- A responsive dashboard with charts and status indicators
- 1–30-year projections for growth, traffic, water, and waste
- Scenario Lab to compare proposed improvements against the current city
- PDF report and forecast CSV export
- Save/load scenario JSON files; sample data / reset
- Safeguards for invalid numbers and unreadable JSON files

### Where the teacher-required Python concepts are used

| Teacher requirement | Demonstration in source code |
|---|---|
| Python | All calculations in `city_engine.py`; interface in `app.py` |
| Functions | `traffic_management()`, `water_management()`, `construction_estimator()`, `waste_management()`, `calculate_city()` |
| Loops | `validate_city()` loops over inputs; `forecast_city()` iterates over years |
| Conditionals | Traffic classification, water status, waste recommendations |
| Menu interface | Sidebar module navigation in `app.py` |
| Input validation | `_number()` / `validate_city()` and constrained number input widgets |
| Invalid input handling | `ValueError` with messages and JSON import exception handling |
| Meaningful comments | Explanation of formulas, assumptions and control flow in each file |

## Formulas and classroom assumptions

**Traffic density** = vehicles / road length in km. The task brief specifies the four categories but does not give numeric thresholds, so this app uses an explicitly declared classroom convention: Low ≤ 25, Moderate > 25–60, High > 60–100, Critical > 100 vehicles/km.

**Water demand** = population × **135 litres per person per day** (exactly as the teacher requires).

**Water balance** = available daily supply − demand. Negative = shortage; positive = surplus.

**Total floor area** = building length × building width × number of floors.

**Total construction budget** = total floor area × user-entered cost per m². Currency shown in PKR. This is a simplified classroom estimate, not a commercial cost estimate.

**Daily waste** = population × waste per person (kg/day).

**Waste to recycle** = total daily waste × recycling percentage / 100.

**City health index**: an *illustrative* weighted index based on classroom traffic severity (35%), water coverage (40%) and recycling percentage (25%). This is **not** a real official city rating.

**Future planning**: applies annual compound growth rates chosen by the user; these are scenarios, not real-world sensor measurements or official forecasts.

## Run automated tests

```bash
python -m unittest discover -s tests -v
```

Tests cover required module calculations, category boundaries, input validation, projections, and PDF generation.

## File structure

- `app.py` — Streamlit user interface, navigation, forms, charts, scenario lab.
- `city_engine.py` — **pure Python functions** for calculations and validation.
- `reports.py` — creates the downloadable PDF report in Python.
- `requirements.txt` — libraries to install.
- `.streamlit/config.toml` — UI theme configuration.
- `tests/test_city_engine.py` — unit tests.
- `sample_scenario.json` — starter file that can be imported into the app.

## Presentation and lab viva

1. Open **Overview** and point out the four KPIs.
2. Visit **Traffic**; change vehicles and show how severity/action changes.
3. Visit **Water**; demonstrate a shortage by reducing supply.
4. Visit **Construction**; change number of floors to increase budget.
5. Visit **Waste**; change recycling percentage and inspect the chart.
6. Show **Future Planning** and **Scenario Lab** as extra innovations.
7. Open **City Report** and download the PDF.
8. Explain that math is implemented in Python functions (`city_engine.py`), not browser JavaScript.

*Original design and project code. The classmate's HTML file was used only as a high-level example; it is not required to run this project.*

## Streamlit Community Cloud deployment

Use Python **3.12** for this deployment. The three direct dependencies are pinned
in `requirements.txt`; `app.py` is the repository-root entry point. No secrets,
external services, system packages, or writable persistent disk are required.

Deployment settings:

- Repository: your GitHub account's `civitas-smart-city` repository
- Branch: `main`
- Main file path: `app.py`
- Python: **3.12**, selected in **Advanced settings** before deployment
- App URL: `civitas-smart-city` if available, otherwise an available alternative

`.python-version` records the local test runtime. Community Cloud's Python
version must be selected in Advanced settings; that file does not configure it.

Before pushing updates, install the pinned dependencies and run:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Commit and push edits to `main` on GitHub. Community Cloud automatically updates
the app from that branch and reinstalls dependencies when requirements change.
Keep `.streamlit/secrets.toml`, `.env` files, credentials, and local caches out of
Git. Scenario inputs belong to each browser session and are not shared between
visitors; use Export scenario JSON to save them.