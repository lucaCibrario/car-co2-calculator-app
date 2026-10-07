# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 17:33:24 2025

@author: lucac
"""
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QTimer
import plotly.graph_objs as go
from plotly.offline import plot
from plotly.colors import qualitative
from PySide6.QtWidgets import QSizePolicy, QMessageBox

from numpy import arange, concatenate
import numpy as np

import src


class PlotlyWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.loadFinished.connect(self.on_load_finished)

        self.plotKilometers = go.Figure()
        self.plotYears = go.Figure()

        # Create layout and web view
        self.setContentsMargins(0, 0, 0, 5)

        # Create and load Plotly figure
        self.initialize_empty_plots()

        self.page().loadFinished.connect(self._on_load_finished)

    def plot_co2_hystory(self):
        self.generalSettings = self.parent.generalSettings
        self.currentCarData = self.parent.currentCarData
        self.carData = self.parent.carData
        self.data = self.parent.data

        self.plotKilometers = go.Figure()
        self.plotYears = go.Figure()

        lifeSpanThresholdICE = self.generalSettings['ICElifeSpan']
        lifeSpanThresholdBEV = self.generalSettings['BEVlifeSpan']
        conversionFactor = self.generalSettings['km2yearsConvFactor']
        self.plotSpan = max(lifeSpanThresholdICE, lifeSpanThresholdBEV) * 1.4 + self.currentCarData["mileage"]

        secondHandMileage_currentCar = self.carData[0]['secondHandCarMileage'] if self.carData[0]['secondHandCarMileage'] else 0
        secondHandAge_currentCar = self.carData[0]['secondHandCarAge'] if self.carData[0]['secondHandCarAge'] else 0

        self.analysisStartKm = secondHandMileage_currentCar
        self.analysisStartYears = secondHandAge_currentCar

        self.analysisStartKm = round(self.analysisStartKm, -3)
        self.plotSpan = round(self.plotSpan, -3)
        plotXaxis = arange(self.analysisStartKm, self.plotSpan + 1, 1000)

        for carIndex in range(len(self.carData)):

            if carIndex == 0:
                if not self.validate_current_car_data():
                    return 0

            if carIndex == 0:
                startMileage = self.analysisStartKm
                label = f"Current car ({self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']})"
            else:
                startMileage = self.currentCarData["mileage"]
                label = f"Car {carIndex} ({self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']})"

            # Filter plotXaxis to only include values >= startMileage
            valid_mask = plotXaxis >= startMileage
            valid_plotXaxis = plotXaxis[valid_mask]
            self.carData[carIndex]['xValues'] = valid_plotXaxis

            # Compute emissions only for valid values
            emissions = self.carData[carIndex]['usePhaseEmissions'] * (valid_plotXaxis - startMileage) / 1e6

            secondHandMileage = self.carData[carIndex]['secondHandCarMileage'] if self.carData[carIndex]['secondHandCarMileage'] else 0
            secondHandAge = self.carData[carIndex]['secondHandCarAge'] if self.carData[carIndex]['secondHandCarAge'] else 0

            # Maintenance and degradation
            if self.generalSettings['maintenance']:
                # Case with ordinary maintenance
                # degradation
                multipliers = src.Utilities.add_degradation(valid_plotXaxis - startMileage + secondHandMileage,
                                                            1.005,
                                                            conversionFactor)
                emissions = emissions * multipliers
                self.carData[carIndex]['totalUsePhaseEmissions'] = emissions

                # maintenance
                maintenanceData = self.data['maintenance']
                emissions = src.Utilities.add_maintenance(self.data,
                                                          valid_plotXaxis - startMileage + secondHandMileage,
                                                          emissions,
                                                          self.carData[carIndex]['depreciation'])
                self.carData[carIndex]['totalUsePhaseEmissionsPlusMaintenance'] = emissions

            else:
                # case without maintenance
                # degradation
                multipliers = src.Utilities.add_degradation(valid_plotXaxis - startMileage + secondHandMileage,
                                                            1.01,
                                                            conversionFactor)
                emissions = emissions * multipliers
                self.carData[carIndex]['totalUsePhaseEmissions'] = emissions
                self.carData[carIndex]['totalUsePhaseEmissionsPlusMaintenance'] = emissions

            # Add the emissions of the current car at the moment of the replacement (only for new cars)
            if carIndex != 0:
                emissions = emissions + self.emissionsCurrentCar

            # Add production and EoL contribution
            emissions = emissions + self.carData[carIndex]['productionEoL'] / 1e6

            # Add battery replacement contribution (only for BEV)
            if self.carData[carIndex]['engineType'] == 'BEV':
                battery_capacity = self.carData[carIndex]['batteryCapacity']
                battery_footprint = self.carData[carIndex]['batteryProductionFootprint']
                battery_life_km = self.carData[carIndex]['batteryLifeTime']

                self.carData[carIndex]['batteryReplacementLog'] = add_battery_replacement_emissions(
                    valid_plotXaxis,
                    startMileage,
                    battery_life_km,
                    battery_capacity,
                    battery_footprint,
                    secondHandMileage
                )

                emissions += self.carData[carIndex]['batteryReplacementLog']

            # Define cutoff for solid vs dashed line
            if carIndex == 0:
                # life span for current car
                if self.carData[carIndex]['engineType'] == 'BEV':
                    cutoffMileage = lifeSpanThresholdBEV
                else:
                    cutoffMileage = lifeSpanThresholdICE

            else:
                # life span for new cars
                if self.carData[carIndex]['engineType'] == 'BEV':
                    cutoffMileage = startMileage + lifeSpanThresholdBEV - secondHandMileage
                else:
                    cutoffMileage = startMileage + lifeSpanThresholdICE - secondHandMileage

                # condition if the new car is kept only for a limited amount of kilometers
                # if not self.carData[carIndex]['keepEOL']:
                cutoffMileage = min(
                    cutoffMileage, self.carData[carIndex]['keepLifeSpan'] * conversionFactor + startMileage)

            self.carData[carIndex]['carLifeSpan'] = cutoffMileage

            # Find indices for solid and dashed parts
            solid_mask = valid_plotXaxis <= cutoffMileage
            dashed_mask = valid_plotXaxis > cutoffMileage

            self.update_plot_kilometers(valid_plotXaxis, emissions,
                                        label, solid_mask, dashed_mask, carIndex, startMileage)

            plotYears_xValues = (valid_plotXaxis - secondHandMileage_currentCar) / conversionFactor + secondHandAge_currentCar
            startAge = (startMileage - secondHandMileage_currentCar) / conversionFactor + secondHandAge_currentCar

            self.update_plot_years(plotYears_xValues, emissions,
                                   label, solid_mask, dashed_mask, carIndex, startAge)

            # store emission data for analysis in tables
            self.carData[carIndex]['emissionHystory'] = emissions
            if carIndex == 0:
                if self.currentCarData["secondHandCarMileage"]:
                    self.emissionsCurrentCar = emissions[int(
                        round((self.currentCarData["mileage"] - self.currentCarData["secondHandCarMileage"]) / 1000))]
                else:
                    self.emissionsCurrentCar = emissions[int(
                        round(self.currentCarData["mileage"] / 1000))]

        # computation of xlim and ylim
        maxWindowYears = self.parent.maxWindowYears
        maxWindowKm = (maxWindowYears - secondHandAge_currentCar) * conversionFactor + secondHandMileage_currentCar
        carsEoLKm = min([self.carData[i]["carLifeSpan"] for i in range(len(self.carData))])

        self.xmaxRangeKm = min(maxWindowKm, carsEoLKm)
        self.xminRangeKm = self.analysisStartKm - 500

        self.thMileage = [self.xminRangeKm / 1000, self.xmaxRangeKm / 1000]
        self.thAge = [self.analysisStartYears - 0.02,
                      (self.xmaxRangeKm - secondHandMileage_currentCar) / conversionFactor + secondHandAge_currentCar]

        # if self.thAge[1] > maxWindowYears:
        #     self.thAge[1] = maxWindowYears
        #     self.thMileage[1] = ((self.thAge[1] - secondHandAge_currentCar) * conversionFactor + secondHandMileage_currentCar) / 1000

        self.update_ylim()

        self.addThresholdLine()

        self.update_plot_kilometers_layout(self.thMileage,
                                           self.yRange)
        # self.update_plot_years_layout([self.xminRangeKm / conversionFactor, self.xmaxRangeKm / conversionFactor],
        #                               self.yRange)
        self.update_plot_years_layout(self.thAge,
                                      self.yRange)

        return 1

    def initialize_empty_plots(self):
        # Initilize empty plot kilometers
        self.plotKilometers = go.Figure()
        self.plotKilometers.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Empty'))

        self.update_plot_kilometers_layout([0, 200], [0, 90])

        # Initilize empty plot years
        self.plotYears = go.Figure()
        self.plotYears.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Empty'))

        self.update_plot_years_layout([0, 20], [0, 90])

    def show_plot_kilometers(self):
        toBePlotted = self.plotKilometers
        self.refresh_plot(toBePlotted)

    def show_plot_years(self):
        toBePlotted = self.plotYears
        self.refresh_plot(toBePlotted)

    def refresh_plot(self, toBePlotted):

        html = plot(toBePlotted,
                    include_plotlyjs='cdn',
                    output_type='div',
                    config={'scrollZoom': True,
                            'displayModeBar': True,
                            'displaylogo': False,
                            'responsive': True,
                            'modeBarButtonsToRemove': ['toImage']
                            })
        # self.setHtml(html)
        super().setHtml(html)
        QTimer.singleShot(1000, self._delayed_repaint)

    def _on_load_finished(self, ok):
        if ok:
            # Delay a tiny bit to allow Chromium to finish painting
            QTimer.singleShot(1000, self._delayed_repaint)

    def _delayed_repaint(self):
        self.resize(self.width() + 1, self.height())  # Force a micro-resize
        self.resize(self.width() - 1, self.height())  # Back to original

    def update_plot_kilometers_layout(self, xrange, yrange):
        self.plotKilometers.update_layout(
            title=dict(text='CO<sub>2</sub> Footprint History', x=0.5, xanchor='center'),
            autosize=True,
            xaxis=dict(
                title='Current Car Mileage (1000 km)',
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=xrange
            ),
            yaxis=dict(
                title='tCO₂<sub>eq</sub>',
                showgrid=True,
                gridwidth=1,
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=yrange
            ),
            hovermode='x',
            dragmode='pan',
            legend=dict(
                font=dict(size=10),
                x=0,
                y=1,
                xanchor='left',
                yanchor='top',
                # bgcolor='rgba(255,255,255,0.5)',  # optional
                bordercolor='gray',
                # borderwidth=1
            ),
            margin=dict(l=20, r=20, t=35, b=20),
        )

    def update_plot_years_layout(self, xrange, yrange):
        self.plotYears.update_layout(
            title=dict(text='CO<sub>2</sub> Footprint History', x=0.5, xanchor='center'),
            autosize=True,
            xaxis=dict(
                title='Current Car Age (years)',
                showgrid=True,
                # gridcolor='lightgray',
                gridwidth=1,
                # griddash='dash',
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=xrange
                # dtick=50
            ),
            yaxis=dict(
                title='tCO₂<sub>eq</sub>',
                showgrid=True,
                # gridcolor='lightgray',
                gridwidth=1,
                # griddash='dash',
                zeroline=False,
                tickwidth=1,
                fixedrange=False,
                range=yrange
                # dtick=10
            ),
            # plot_bgcolor='white',
            # paper_bgcolor='white',
            hovermode='x',
            dragmode='pan',
            legend=dict(
                font=dict(size=10),
                x=0,
                y=1,
                xanchor='left',
                yanchor='top',
                # bgcolor='rgba(255,255,255,0.5)',  # optional
                bordercolor='gray',
                # borderwidth=1
            ),
            margin=dict(l=20, r=20, t=35, b=20),
        )

    def update_plot_kilometers(self, x, y, label, solid, dashed, carIndex, startMileage):

        line_color = qualitative.Plotly[carIndex % len(qualitative.Plotly)]

        self.plotKilometers.add_trace(go.Scatter(
            x=x[solid] / 1000,
            y=y[solid],
            mode='lines',
            name=label,
            line=dict(dash='solid', color=line_color)
        ))

        if any(dashed):
            x_dashed = np.insert(x[dashed], 0, x[solid][-1])
            y_dashed = np.insert(y[dashed], 0, y[solid][-1])
            self.plotKilometers.add_trace(go.Scatter(
                x=x_dashed / 1000,
                y=y_dashed,
                mode='lines',
                line=dict(dash='dash', color=line_color),
                name=label,
                showlegend=False,
            ))

        self.plotKilometers.add_shape(
            type='line',
            x0=startMileage / 1000,
            x1=startMileage / 1000,
            y0=0 if carIndex == 0 else self.emissionsCurrentCar,
            y1=y[0],
            line=dict(color=line_color),
            xref='x',
            yref='y'
        )

    def update_plot_years(self, x, y, label, solid, dashed, carIndex, startMileage):

        line_color = qualitative.Plotly[carIndex % len(qualitative.Plotly)]

        self.plotYears.add_trace(go.Scatter(
            x=x[solid],
            y=y[solid],
            mode='lines',
            name=label,
            line=dict(dash='solid', color=line_color)
        ))

        if any(dashed):
            x_dashed = np.insert(x[dashed], 0, x[solid][-1])
            y_dashed = np.insert(y[dashed], 0, y[solid][-1])
            self.plotYears.add_trace(go.Scatter(
                x=x_dashed,
                y=y_dashed,
                mode='lines',
                line=dict(dash='dash', color=line_color),
                name=label,
                showlegend=False,
            ))

        self.plotYears.add_shape(
            type='line',
            x0=startMileage,
            x1=startMileage,
            y0=0 if carIndex == 0 else self.emissionsCurrentCar,
            y1=y[0],
            line=dict(color=line_color),
            xref='x',
            yref='y'
        )

    def update_ylim(self):
        xmin = self.analysisStartKm
        xmax = self.xmaxRangeKm

        y_visible = []

        for carIndex in range(len(self.carData)):
            x_vals = self.carData[carIndex]['xValues']
            y_vals = self.carData[carIndex]['emissionHystory']

            for x, y in zip(x_vals, y_vals):
                if xmin <= x <= xmax:
                    y_visible.append(y)

        y_visible.append(0)
        if y_visible:
            ymin = min(y_visible)
            ymax = max(y_visible)

            margin = 0.1 * (ymax - ymin) if ymax > ymin else 1.0  # prevent collapse
            self.yRange = [ymin, ymax + margin]
        else:
            # Default range if no data is in view
            self.yRange = [0, 90]

    def addThresholdLine(self):
        maxY = max([self.carData[carIndex]['emissionHystory'][-1] for carIndex in range(len(self.carData))])
        self.plotKilometers.add_shape(
            type='line',
            x0=self.thMileage[1],
            x1=self.thMileage[1],
            y0=self.yRange[0],
            y1=maxY,
            line=dict(color='gray', width=1, dash='dot'),
            xref='x',
            yref='y'
        )

        self.plotYears.add_shape(
            type='line',
            x0=self.thAge[1],
            x1=self.thAge[1],
            y0=self.yRange[0],
            y1=maxY,
            line=dict(color='gray', width=1, dash='dot'),
            xref='x',
            yref='y'
        )

        self.plotKilometers.add_annotation(
            x=self.thMileage[1],
            y=self.yRange[0],  # near bottom of y-axis
            text=f"EoU = {self.thMileage[1]*1000:,.0f} km",
            showarrow=False,
            yshift=10,  # slight shift upward to avoid overlapping x-axis
            font=dict(color='gray', size=12),
            xanchor="right"
        )

        self.plotYears.add_annotation(
            x=self.thAge[1],
            y=self.yRange[0],
            text=f"EoU = {self.thAge[1]:.1f} years",
            showarrow=False,
            yshift=10,
            font=dict(color='gray', size=12),
            xanchor="right"
        )

    def validate_current_car_data(self):
        conversionFactor = self.generalSettings['km2yearsConvFactor']
        mileageToChange = self.currentCarData["mileage"] - self.analysisStartKm
        yearsOfCurrentUser = self.parent.maxWindowYears - self.analysisStartYears
        maxAllowedMileage = yearsOfCurrentUser * conversionFactor

        if mileageToChange > maxAllowedMileage:
            QMessageBox.warning(self,
                                "Invalid Input",
                                "The current car cannot reach the defined mileage for the change because it gets too old.\n"
                                f"The maximum allowed life for the current car is set to {self.parent.maxWindowYears} years.\n\n"
                                "Please consider adjusting one or more of the following inputs:\n"
                                "- Current Mileage (km)\n"
                                "- Average Annual Mileage\n"
                                "- Second-hand Car Mileage (km)\n"
                                "- Second-hand Car Age (years) (only if the car is second-hand)"
                                )
            return 0

        else:
            return 1


def add_battery_replacement_emissions(x_axis_km,
                                      start_km,
                                      battery_life_km,
                                      capacity,
                                      footprint,
                                      secondHandMileage=0):
    import numpy as np
    replacementLog = np.zeros(len(x_axis_km))
    replacement_value = capacity * footprint / 1000  # tCO₂ per battery replacement
    battery_life_km = round(battery_life_km, -3)
    next_replacement_km = start_km + battery_life_km - secondHandMileage

    while next_replacement_km <= x_axis_km[-1]:
        index = np.searchsorted(x_axis_km, next_replacement_km)
        if index + 1 < len(x_axis_km):
            replacementLog[index + 1:] += replacement_value
        next_replacement_km += battery_life_km

    return replacementLog
