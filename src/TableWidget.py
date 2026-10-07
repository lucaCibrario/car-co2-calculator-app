# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 06:49:16 2025

@author: lucac
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from src.Utilities import interp_data
from PySide6.QtGui import QFont, QPen, QPainter


class TableWidgetEOU(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._isEmpty = True
        self.setContentsMargins(0, 0, 0, 0)

        self.itemFontSmall = QFont()
        self.itemFontSmall.setPointSize(8)
        self.setFont(self.itemFontSmall)

        self.itemFontBig = QFont()
        self.itemFontBig.setPointSize(9)

        self.parent = parent

        self.setColumnCount(9)

        # self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        self.populate_empty()  # Initialize with empty data

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 70)

        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.setColumnWidth(1, 170)

        for col in range(2, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

        # for col in [0, 1, 4, 5, 6, 7, 8]:
        #     self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
        #     self.setColumnWidth(col, 80)

        # self.setColumnWidth(0, 75)
        # self.setColumnWidth(1, 170)
        # self.setColumnWidth(4, 170)

    def modify_headers(self, ):
        self.setHorizontalHeaderLabels([
            "Car",
            "Car Details",
            "EoU - change\n(tCO₂)",
            "CO₂ Savings\n(tCO₂)",
            "Yearly Emissions\n(tCO₂/year)",
            "Production",
            "EoL",
            "Use",
            "Maintenance",
        ])
        self.horizontalHeaderItem(2).setToolTip(
            "Difference in emissions between the end-of-usage (EoU) and the moment of replacement."
        )
        self.horizontalHeaderItem(3).setToolTip(
            "CO₂ emissions avoided at the end-of-usage period by switching to the new car at the selected age."
        )
        self.horizontalHeaderItem(4).setToolTip(
            "Total estimated yearly emissions from the moment of replacement to the end-of-usage."
        )
        self.horizontalHeaderItem(5).setToolTip(
            "Relative impact of car production on the yearly emissions."
        )
        self.horizontalHeaderItem(6).setToolTip(
            "Relative impact of car end of life (EoL) on the yearly emissions."
        )
        self.horizontalHeaderItem(7).setToolTip(
            "Relative impact of car use phase on the yearly emissions."
        )
        self.horizontalHeaderItem(8).setToolTip(
            "Relative impact of car maintenance on the yearly emissions."
        )

    def populate_empty(self):
        """Populate the output table for BE with data."""
        self._isEmpty = True
        self.modify_headers()

        num_rows = 1  # Exclude the last layout (buttons)
        self.setRowCount(num_rows)

        row = num_rows - 1
        self.set_table_item(row, 0, "")
        self.set_table_item(row, 1, "")
        self.set_table_item(row, 2, "")
        self.set_table_item(row, 3, "")
        self.set_table_item(row, 4, "")
        self.set_table_item(row, 5, "")
        self.set_table_item(row, 6, "")
        self.set_table_item(row, 7, "")
        self.set_table_item(row, 8, "")

    def populate(self):
        """Populate the output table for BE with data."""
        self._isEmpty = False

        self.carData = self.parent.carData

        # populate table
        num_cars = len(self.carData)  # Exclude the last layout (buttons)
        self.setRowCount(num_cars)

        conversionFactor = self.parent.generalSettings['km2yearsConvFactor']

        for row in range(num_cars):
            carIndex = row

            self.set_table_item(row, 0, f'Car {carIndex}' if carIndex != 0 else "Current", self.itemFontBig)

            self.set_table_item(row, 1, f"{self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']}")

            self.set_table_item(row, 2, f"{self.carData[carIndex]['DeltaTHco2']:.1f}", self.itemFontBig)

            if row != 0:
                self.carData[carIndex]["co2Savings"] = self.carData[0]['THco2'] - self.carData[carIndex]['THco2']
                self.set_table_item(row, 3, f"{self.carData[carIndex]['co2Savings']:.1f}", self.itemFontBig)
            else:
                self.carData[carIndex]["co2Savings"] = None
                self.set_table_item(row, 3, "/", self.itemFontBig)

            self.set_table_item(row, 4, f"{self.carData[carIndex]['yearlyCo2']:.2f}", self.itemFontBig)

            prod = self.carData[carIndex]['relativeProductionCo2']
            eol = self.carData[carIndex]['relativeEolCo2']
            use = self.carData[carIndex]['relativeUseCo2']
            mnt = self.carData[carIndex]['relativeMaintenanceCo2']

            # Round the first three
            prod_r = round(prod, 1)
            eol_r = round(eol, 1)
            use_r = round(use, 1)

            # Determine if maintenance should be displayed and adjusted
            if self.parent.generalSettings["maintenance"]:
                mnt_r = round(100.0 - (prod_r + eol_r + use_r), 1)
            else:
                if self.carData[carIndex]['engineType'] == 'BEV' and mnt != 0:
                    mnt_r = round(100.0 - (prod_r + eol_r + use_r), 1)
                else:
                    mnt_r = None  # not shown, use "/" later
                    # Adjust use to keep total at 100
                    use_r = round(100.0 - (prod_r + eol_r), 1)

            self.carData[carIndex]['relativeProductionCo2'] = prod_r
            self.carData[carIndex]['relativeEolCo2'] = eol_r
            self.carData[carIndex]['relativeUseCo2'] = use_r
            self.carData[carIndex]['relativeMaintenanceCo2'] = mnt_r

            # Set the values
            self.set_table_item(row, 5, f"{prod_r:.1f} %", self.itemFontBig)
            self.set_table_item(row, 6, f"{eol_r:.1f} %", self.itemFontBig)
            self.set_table_item(row, 7, f"{use_r:.1f} %", self.itemFontBig)

            # Maintenance column
            if mnt_r is not None:
                self.set_table_item(row, 8, f"{mnt_r:.1f} %", self.itemFontBig)
            else:
                self.set_table_item(row, 8, "/", self.itemFontBig)

            # self.set_table_item(row, 5, f"{self.carData[carIndex]['relativeProductionCo2']:.1f} %", self.itemFontBig)

            # self.set_table_item(row, 6, f"{self.carData[carIndex]['relativeEolCo2']:.1f} %", self.itemFontBig)

            # self.set_table_item(row, 7, f"{self.carData[carIndex]['relativeUseCo2']:.1f} %", self.itemFontBig)

            # if self.parent.generalSettings["maintenance"]:
            #     self.set_table_item(row, 8, f"{self.carData[carIndex]['relativeMaintenanceCo2']:.1f} %", self.itemFontBig)
            # else:
            #     if self.carData[carIndex]['engineType'] == 'BEV' and self.carData[carIndex]['relativeMaintenanceCo2'] != 0:
            #         self.set_table_item(row, 8, f"{self.carData[carIndex]['relativeMaintenanceCo2']:.1f} %", self.itemFontBig)
            #     else:
            #         self.set_table_item(row, 8, f"/", self.itemFontBig)

    def set_table_item(self, row, col, text, font=None):
        item = QTableWidgetItem(text)
        if font:
            item.setFont(font)
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)


class TableWidgetBE(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._isEmpty = True
        self.setContentsMargins(0, 0, 0, 0)

        self.parent = parent

        self.setColumnCount(6)

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        self.populate_empty(parent.unit_combo.read())  # Initialize with empty data

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 100)

        for col in range(1, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

    def modify_headers(self, units):
        if units == 'km':
            self.setHorizontalHeaderLabels([
                r"Car",
                r"Car Details",
                r"Mileage at BEP (km)",
                r"Emissions at BEP (t CO₂)",
                r"BEP - change (km)",
                r"BEP - change (t CO₂)"
            ])
            self.horizontalHeaderItem(2).setToolTip(
                "Mileage at which the new car's cumulative emissions equal those of the current car."
            )
            self.horizontalHeaderItem(3).setToolTip(
                "Total emissions at the break-even point (BEP)."
            )
            self.horizontalHeaderItem(4).setToolTip(
                "Difference in mileage between BEP and the moment of replacement."
            )
            self.horizontalHeaderItem(5).setToolTip(
                "Difference in emissions between BEP and the moment of replacement."
            )
        else:
            self.setHorizontalHeaderLabels([
                r"Car",
                r"Car Details",
                r"Age at BEP (years)",
                r"Emissions at BEP (t CO₂)",
                r"BEP - change (years)",
                r"BEP - change (t CO₂)"
            ])
            self.horizontalHeaderItem(2).setToolTip(
                "Age at which the new car's cumulative emissions equal those of the current car."
            )
            self.horizontalHeaderItem(3).setToolTip(
                "Total emissions at the break-even point (BEP)."
            )
            self.horizontalHeaderItem(4).setToolTip(
                "Difference in age between BEP and the moment of replacement."
            )
            self.horizontalHeaderItem(5).setToolTip(
                "Difference in emissions between BEP and the moment of replacement."
            )

    def populate_empty(self, units):
        """Populate the output table for BE with data."""
        self._isEmpty = True
        self.modify_headers(units)

        num_rows = 1  # Exclude the last layout (buttons)
        self.setRowCount(num_rows)

        row = num_rows - 1
        self.setItem(row, 0, QTableWidgetItem(""))
        self.setItem(row, 1, QTableWidgetItem(""))
        self.setItem(row, 2, QTableWidgetItem(""))
        self.setItem(row, 3, QTableWidgetItem(""))
        self.setItem(row, 4, QTableWidgetItem(""))
        self.setItem(row, 5, QTableWidgetItem(""))

    def populate(self, units):
        """Populate the output table for BE with data."""
        self._isEmpty = False
        self.modify_headers(units)

        self.carData = self.parent.carData

        # populate table
        num_cars = len(self.carData) - 1  # Exclude the last layout (buttons)
        self.setRowCount(num_cars)

        conversionFactor = self.parent.generalSettings['km2yearsConvFactor']

        for row in range(num_cars):
            carIndex = row + 1
            if self.carData[carIndex]['BEkm']:

                # Car label
                item = QTableWidgetItem(f'Car {carIndex}')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 0, item)

                # Car details
                item = QTableWidgetItem(
                    f"{self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']}")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 1, item)

                if units == 'km':
                    item = QTableWidgetItem(f"{round(self.carData[carIndex]['BEkm'], -3):,.0f}")
                else:
                    item = QTableWidgetItem(
                        f"{self.carData[carIndex]['BEkm']/conversionFactor:.1f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, item)

                item = QTableWidgetItem(str(round(self.carData[carIndex]['BEco2'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 3, item)

                if units == 'km':
                    item = QTableWidgetItem(
                        f"{round(self.carData[carIndex]['DeltaBEkm'], -3):,.0f}")
                else:
                    item = QTableWidgetItem(
                        f"{self.carData[carIndex]['DeltaBEkm']/conversionFactor:.1f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 4, item)

                item = QTableWidgetItem(str(round(self.carData[carIndex]['DeltaBEco2'])))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 5, item)

            else:
                item = QTableWidgetItem(f'Car {carIndex}')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 0, item)

                item = QTableWidgetItem(
                    f"{self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']}")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 1, item)

                item = QTableWidgetItem('No BE point')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, item)

                item = QTableWidgetItem('/')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 3, item)

                item = QTableWidgetItem('/')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 4, item)

                item = QTableWidgetItem('/')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 5, item)


class TableWidgetMileage(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self._isEmpty = True
        self.parent = parent

        self.setColumnCount(4)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 100)

        for col in range(1, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

        self.populate_empty(parent.unit_combo.read())

    def modify_headers(self, units):
        if units == 'km':
            self.setHorizontalHeaderLabels(
                ["Car",
                 r"Car Details",
                 "CO₂ Savings (t CO₂)",
                 "Distance from BE (km)"]
            )
            self.horizontalHeaderItem(2).setToolTip(
                "CO₂ emissions avoided by switching to the new car at the selected mileage."
            )
            self.horizontalHeaderItem(3).setToolTip(
                "How far (in km) the selected point is from the BEP."
            )
        else:
            self.setHorizontalHeaderLabels(
                ["Car",
                 r"Car Details",
                 "CO₂ Savings (t CO₂)",
                 "Distance from BE (years)"]
            )
            self.horizontalHeaderItem(2).setToolTip(
                "CO₂ emissions avoided by switching to the new car at the selected age."
            )
            self.horizontalHeaderItem(3).setToolTip(
                "How far (in years) the selected point is from the BEP."
            )

    def populate_empty(self, units):
        """Populate the output table for BE with data."""
        self._isEmpty = True
        self.modify_headers(units)

        num_rows = 1  # Exclude the last layout (buttons)
        self.setRowCount(num_rows)

        row = num_rows - 1
        self.setItem(row, 0, QTableWidgetItem(""))
        self.setItem(row, 1, QTableWidgetItem(""))
        self.setItem(row, 2, QTableWidgetItem(""))
        self.setItem(row, 3, QTableWidgetItem(""))

    def populate(self, units):
        self._isEmpty = False
        self.modify_headers(units)
        self.carData = self.parent.carData

        inputText = self.parent.specifyMileage_lineEdit.read()
        conversionFactor = self.parent.generalSettings['km2yearsConvFactor']
        if units == 'km':
            mileage = int(inputText)  # Get the user-specified mileage
        else:
            mileage = int(inputText) * conversionFactor

        num_cars = len(self.carData) - 1  # Include the original car
        self.setRowCount(num_cars)

        co2AtMileageOldCar = interp_data(
            self.carData[0]['xValues'], self.carData[0]['emissionHystory'], mileage)

        for row in range(num_cars):

            carIndex = row + 1
            co2AtMileageCurrentCar = interp_data(
                self.carData[carIndex]['xValues'], self.carData[carIndex]['emissionHystory'], mileage)

            # Car Label
            item = QTableWidgetItem(f"Car {carIndex}")
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item)

            # Car data (segment - engine)
            item = QTableWidgetItem(
                f"{self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']}")
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item)

            # CO₂ savings
            item = QTableWidgetItem(
                str(round(float(co2AtMileageOldCar - co2AtMileageCurrentCar))))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(
                row, 2, item)

            # Distance from BE point
            if self.carData[carIndex]['BEkm']:
                delta = mileage - self.carData[carIndex]['BEkm']

                if units == 'km':
                    item = QTableWidgetItem(f"{round(delta, -3):,.0f}")
                else:
                    item = QTableWidgetItem(f"{delta/conversionFactor:.1f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(
                    row, 3, item)
            else:
                item = QTableWidgetItem('No BE point')
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 3, item)
