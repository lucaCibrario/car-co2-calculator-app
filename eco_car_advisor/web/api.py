"""HTTP endpoints for the local web application."""

from io import BytesIO, StringIO
from pathlib import Path

import markdown
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eco_car_advisor.analysis import AnalysisInputError
from eco_car_advisor.data import load_assumptions
from eco_car_advisor.export import build_export_frame
from eco_car_advisor.resources import resource_path
from eco_car_advisor.tooltips import tooltips
from eco_car_advisor.web.service import analyze, result_payload, vehicle_defaults

STATIC = Path(__file__).parent / "static"
PLOTLY_JS = Path(__import__("plotly").__file__).parent / "package_data" / "plotly.min.js"


class Vehicle(BaseModel):
    """Vehicle fields accepted from the browser."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    carSegment: str
    engineType: str
    massValue: float = Field(gt=0, le=100_000)
    carProductionFootprint: float = Field(ge=0, le=100_000)
    WTT: float | None = Field(default=None, ge=0, le=100_000)
    TTW: float | None = Field(default=None, ge=0, le=100_000)
    meanConsumptionLiter: float | None = Field(default=None, gt=0, le=1000)
    meanConsumptionWh: float | None = Field(default=None, gt=0, le=1000)
    drivingShare: float | None = Field(default=None, ge=0, le=1)
    secondHandCar: bool = False
    secondHandCarMileage: float | None = Field(default=None, ge=0, le=1_000_000)
    secondHandCarAge: float | None = Field(default=None, ge=0, le=100)
    batteryCapacity: float | None = Field(default=None, gt=0, le=10_000)
    batteryProductionFootprint: float | None = Field(default=None, ge=0, le=100_000)
    batteryLifeTime: float | None = Field(default=None, ge=500, le=1_000_000)
    country: str | None = None
    energyMix: float | None = Field(default=None, ge=0, le=10_000)
    mileage: float | None = Field(default=None, ge=0, le=1_000_000)

    @model_validator(mode="after")
    def validate_vehicle(self):
        assumptions = load_assumptions()
        if self.carSegment not in assumptions["car_segments"]:
            raise ValueError("Unknown vehicle segment")
        if self.engineType not in assumptions["engine_types"]:
            raise ValueError("Unknown engine type")
        if self.secondHandCar:
            if self.secondHandCarMileage is None or self.secondHandCarAge is None:
                raise ValueError("Second-hand mileage and age are required")
        else:
            self.secondHandCarMileage = None
            self.secondHandCarAge = None
        required = ["massValue", "carProductionFootprint"]
        if self.engineType == "BEV":
            required += [
                "meanConsumptionWh",
                "batteryCapacity",
                "batteryProductionFootprint",
                "batteryLifeTime",
            ]
        else:
            required += ["meanConsumptionLiter", "WTT", "TTW"]
            if self.engineType == "Plug-in Hybrid":
                required += ["meanConsumptionWh", "drivingShare"]
        for name in required:
            if getattr(self, name) is None:
                raise ValueError(f"{name} is required for {self.engineType}")
        return self


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    ICElifeSpan: float = Field(gt=0, le=1_000_000)
    BEVlifeSpan: float = Field(gt=0, le=1_000_000)
    km2yearsConvFactor: float = Field(gt=0, le=100_000)
    maintenance: bool
    keepEOL: bool
    keepLifeSpan: float | None = Field(default=None, gt=0, le=1_000_000)
    keepUnits: str

    @field_validator("keepUnits")
    @classmethod
    def validate_units(cls, value: str) -> str:
        if value not in ("km", "years"):
            raise ValueError("End-of-usage units must be km or years")
        return value

    @model_validator(mode="after")
    def validate_end_of_usage(self):
        if not self.keepEOL and self.keepLifeSpan is None:
            raise ValueError("An intended end of usage is required")
        if self.keepEOL:
            self.keepLifeSpan = None
        return self


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    current: Vehicle
    alternatives: list[Vehicle] = Field(min_length=1, max_length=8)
    settings: Settings

    @model_validator(mode="after")
    def validate_current(self):
        current = self.current
        if current.mileage is None:
            raise ValueError("Current mileage is required")
        if current.country not in load_assumptions()["countries"]:
            raise ValueError("Unknown country")
        if current.energyMix is None:
            raise ValueError("Current energy mix is required")
        if current.country != "Custom":
            expected_mix = round(
                load_assumptions()["energy_mix_kg_per_kwh"][current.country] * 1000
            )
            if current.energyMix != expected_mix:
                raise ValueError("Electricity mix must match the selected country")
        lifespan = (
            self.settings.BEVlifeSpan if current.engineType == "BEV" else self.settings.ICElifeSpan
        )
        if current.mileage >= lifespan:
            raise ValueError("Current mileage must be below the vehicle lifespan")
        if (
            current.secondHandCar
            and current.secondHandCarAge >= load_assumptions()["max_window_years"]
        ):
            raise ValueError("Second-hand car age exceeds the analysis window")
        return self


def run_scenario(scenario: Scenario):
    try:
        return analyze(
            scenario.current.model_dump(),
            [
                car.model_dump(exclude={"country", "energyMix", "mileage"})
                for car in scenario.alternatives
            ],
            scenario.settings.model_dump(),
        )
    except (AnalysisInputError, ValueError, ZeroDivisionError, IndexError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


app = FastAPI(title="ECO Car Replacement Advisor", version="1.0.0", docs_url="/api/docs")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/guide", include_in_schema=False)
def guide():
    source = Path(resource_path("Data/Documentation/README.md")).read_text(encoding="utf-8")
    body = markdown.markdown(source, extensions=["tables", "toc", "fenced_code"])
    return HTMLResponse(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>ECO Car Advisor · User guide</title>"
        '<link rel="stylesheet" href="/assets/guide.css"></head>'
        '<body><div class="guide-top"><a href="/">← Back to analysis</a>'
        '<span>FAAS MEMBER TOOL</span></div><main class="guide">'
        f"{body}</main></body></html>"
    )


@app.get("/assets/plotly.min.js", include_in_schema=False)
def plotly_script():
    return FileResponse(PLOTLY_JS, media_type="text/javascript")


@app.get("/api/config")
def config():
    assumptions = load_assumptions()
    return {
        "segments": assumptions["car_segments"],
        "engines": assumptions["engine_types"],
        "countries": assumptions["countries"],
        "energyMix": {
            key: round(value * 1000) for key, value in assumptions["energy_mix_kg_per_kwh"].items()
        },
        "defaults": {
            "current": vehicle_defaults("Segment B", "Gasoline (Euro 6)", current=True),
            "replacement": vehicle_defaults("Segment B", "Gasoline (Euro 6)"),
            "settings": {
                "ICElifeSpan": assumptions["default_ice_lifespan_km"],
                "BEVlifeSpan": assumptions["default_bev_lifespan_km"],
                "km2yearsConvFactor": assumptions["default_annual_mileage_km"],
                "maintenance": True,
                "keepEOL": True,
                "keepLifeSpan": None,
                "keepUnits": "years",
            },
        },
        "tooltips": tooltips(),
        "maxWindowYears": assumptions["max_window_years"],
    }


@app.get("/api/vehicle-defaults")
def defaults(segment: str = Query(), engine: str = Query()):
    try:
        return vehicle_defaults(segment, engine)
    except (ValueError, KeyError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/analyze")
def analyze_endpoint(scenario: Scenario):
    return result_payload(run_scenario(scenario))


@app.post("/api/export/{format_name}")
def export_endpoint(format_name: str, scenario: Scenario):
    if format_name not in ("csv", "xlsx"):
        raise HTTPException(status_code=404, detail="Unsupported export format")
    frame = build_export_frame(run_scenario(scenario))
    if format_name == "csv":
        stream = StringIO()
        frame.to_csv(stream, index=False)
        data = stream.getvalue().encode("utf-8-sig")
        media_type = "text/csv; charset=utf-8"
    else:
        stream = BytesIO()
        frame.to_excel(stream, index=False)
        data = stream.getvalue()
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return Response(
        data,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="car_data_export.{format_name}"'},
    )


app.mount("/assets", StaticFiles(directory=STATIC), name="assets")
