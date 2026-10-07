"""Plotly rendering for calculated vehicle emission histories."""

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import plotly.graph_objs as go
from plotly.colors import qualitative
from plotly.offline import plot
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QSizePolicy

from eco_car_advisor.analysis import AnalysisResult


class PlotlyWidget(QWebEngineView):
    """Display analysis histories in either mileage or age units."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._plot_directory = TemporaryDirectory(prefix="eco-car-plots-")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plotKilometers = go.Figure()
        self.plotYears = go.Figure()
        self.setContentsMargins(0, 0, 0, 5)
        self.initialize_empty_plots()
        self.page().loadFinished.connect(self._on_load_finished)

    def render_analysis(self, result: AnalysisResult) -> None:
        """Create both plots from one immutable calculation result."""
        self.plotKilometers = go.Figure()
        self.plotYears = go.Figure()
        self.carData = result.cars
        self.emissionsCurrentCar = result.emissions_at_replacement
        self.analysisStartKm = result.analysis_start_km
        self.analysisStartYears = result.analysis_start_years
        self.xmaxRangeKm = result.end_km
        self.xminRangeKm = result.min_km
        self.thMileage = result.threshold_mileage
        self.thAge = result.threshold_age
        self.yRange = result.y_range
        current = result.current_car
        used_mileage = current["secondHandCarMileage"] or 0
        used_age = current["secondHandCarAge"] or 0
        annual_mileage = result.settings["km2yearsConvFactor"]
        for index, car in enumerate(result.cars):
            start_mileage = result.analysis_start_km if index == 0 else current["mileage"]
            prefix = "Current car" if index == 0 else f"Car {index}"
            label = f"{prefix} ({car['carSegment']} - {car['engineType']})"
            x_values = car["xValues"]
            emissions = car["emissionHystory"]
            solid = x_values <= car["carLifeSpan"]
            dashed = x_values > car["carLifeSpan"]
            self.update_plot_kilometers(
                x_values, emissions, label, solid, dashed, index, start_mileage
            )
            years = (x_values - used_mileage) / annual_mileage + used_age
            start_age = (start_mileage - used_mileage) / annual_mileage + used_age
            self.update_plot_years(years, emissions, label, solid, dashed, index, start_age)
        self.addThresholdLine()
        self.update_plot_kilometers_layout(self.thMileage, self.yRange)
        self.update_plot_years_layout(self.thAge, self.yRange)

    def initialize_empty_plots(self):
        self.plotKilometers = go.Figure()
        self.plotKilometers.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Empty"))
        self.update_plot_kilometers_layout([0, 200], [0, 90])
        self.plotYears = go.Figure()
        self.plotYears.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Empty"))
        self.update_plot_years_layout([0, 20], [0, 90])

    def show_plot_kilometers(self):
        toBePlotted = self.plotKilometers
        self.refresh_plot(toBePlotted)

    def show_plot_years(self):
        toBePlotted = self.plotYears
        self.refresh_plot(toBePlotted)

    def refresh_plot(self, toBePlotted):
        html_path = Path(self._plot_directory.name) / "plot.html"
        plot(
            toBePlotted,
            include_plotlyjs="directory",
            output_type="file",
            filename=str(html_path),
            auto_open=False,
            config={
                "scrollZoom": True,
                "displayModeBar": True,
                "displaylogo": False,
                "responsive": True,
                "modeBarButtonsToRemove": ["toImage"],
            },
        )
        self.load(QUrl.fromLocalFile(str(html_path)))
        QTimer.singleShot(1000, self._delayed_repaint)

    def _on_load_finished(self, ok):
        if ok:
            QTimer.singleShot(1000, self._delayed_repaint)

    def _delayed_repaint(self):
        self.resize(self.width() + 1, self.height())
        self.resize(self.width() - 1, self.height())

    def update_plot_kilometers_layout(self, xrange, yrange):
        self.plotKilometers.update_layout(
            title=dict(text="CO<sub>2</sub> Footprint History", x=0.5, xanchor="center"),
            autosize=True,
            xaxis=dict(
                title="Current Car Mileage (1000 km)",
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=xrange,
            ),
            yaxis=dict(
                title="tCO₂<sub>eq</sub>",
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=yrange,
            ),
            hovermode="x",
            dragmode="pan",
            legend=dict(
                font=dict(size=10),
                x=0,
                y=1,
                xanchor="left",
                yanchor="top",
                bordercolor="gray",
            ),
            margin=dict(l=20, r=20, t=35, b=20),
        )

    def update_plot_years_layout(self, xrange, yrange):
        self.plotYears.update_layout(
            title=dict(text="CO<sub>2</sub> Footprint History", x=0.5, xanchor="center"),
            autosize=True,
            xaxis=dict(
                title="Current Car Age (years)",
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=xrange,
            ),
            yaxis=dict(
                title="tCO₂<sub>eq</sub>",
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=yrange,
            ),
            hovermode="x",
            dragmode="pan",
            legend=dict(
                font=dict(size=10),
                x=0,
                y=1,
                xanchor="left",
                yanchor="top",
                bordercolor="gray",
            ),
            margin=dict(l=20, r=20, t=35, b=20),
        )

    def update_plot_kilometers(self, x, y, label, solid, dashed, carIndex, startMileage):
        line_color = qualitative.Plotly[carIndex % len(qualitative.Plotly)]
        self.plotKilometers.add_trace(
            go.Scatter(
                x=x[solid] / 1000,
                y=y[solid],
                mode="lines",
                name=label,
                line=dict(dash="solid", color=line_color),
            )
        )
        if any(dashed):
            x_dashed = np.insert(x[dashed], 0, x[solid][-1])
            y_dashed = np.insert(y[dashed], 0, y[solid][-1])
            self.plotKilometers.add_trace(
                go.Scatter(
                    x=x_dashed / 1000,
                    y=y_dashed,
                    mode="lines",
                    line=dict(dash="dash", color=line_color),
                    name=label,
                    showlegend=False,
                )
            )
        self.plotKilometers.add_shape(
            type="line",
            x0=startMileage / 1000,
            x1=startMileage / 1000,
            y0=0 if carIndex == 0 else self.emissionsCurrentCar,
            y1=y[0],
            line=dict(color=line_color),
            xref="x",
            yref="y",
        )

    def update_plot_years(self, x, y, label, solid, dashed, carIndex, startMileage):
        line_color = qualitative.Plotly[carIndex % len(qualitative.Plotly)]
        self.plotYears.add_trace(
            go.Scatter(
                x=x[solid],
                y=y[solid],
                mode="lines",
                name=label,
                line=dict(dash="solid", color=line_color),
            )
        )
        if any(dashed):
            x_dashed = np.insert(x[dashed], 0, x[solid][-1])
            y_dashed = np.insert(y[dashed], 0, y[solid][-1])
            self.plotYears.add_trace(
                go.Scatter(
                    x=x_dashed,
                    y=y_dashed,
                    mode="lines",
                    line=dict(dash="dash", color=line_color),
                    name=label,
                    showlegend=False,
                )
            )
        self.plotYears.add_shape(
            type="line",
            x0=startMileage,
            x1=startMileage,
            y0=0 if carIndex == 0 else self.emissionsCurrentCar,
            y1=y[0],
            line=dict(color=line_color),
            xref="x",
            yref="y",
        )

    def addThresholdLine(self):
        maxY = max(
            [self.carData[carIndex]["emissionHystory"][-1] for carIndex in range(len(self.carData))]
        )
        self.plotKilometers.add_shape(
            type="line",
            x0=self.thMileage[1],
            x1=self.thMileage[1],
            y0=self.yRange[0],
            y1=maxY,
            line=dict(color="gray", width=1, dash="dot"),
            xref="x",
            yref="y",
        )
        self.plotYears.add_shape(
            type="line",
            x0=self.thAge[1],
            x1=self.thAge[1],
            y0=self.yRange[0],
            y1=maxY,
            line=dict(color="gray", width=1, dash="dot"),
            xref="x",
            yref="y",
        )
        self.plotKilometers.add_annotation(
            x=self.thMileage[1],
            y=self.yRange[0],
            text=f"EoU = {self.thMileage[1] * 1000:,.0f} km",
            showarrow=False,
            yshift=10,
            font=dict(color="gray", size=12),
            xanchor="right",
        )
        self.plotYears.add_annotation(
            x=self.thAge[1],
            y=self.yRange[0],
            text=f"EoU = {self.thAge[1]:.1f} years",
            showarrow=False,
            yshift=10,
            font=dict(color="gray", size=12),
            xanchor="right",
        )
