"""End-of-usage comparison table."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


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
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.populate_empty()
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 70)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.setColumnWidth(1, 170)
        for col in range(2, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

    def modify_headers(self):
        self.setHorizontalHeaderLabels(
            [
                "Car",
                "Car Details",
                "EoU - change\n(tCO₂)",
                "CO₂ Savings\n(tCO₂)",
                "Yearly Emissions\n(tCO₂/year)",
                "Production",
                "EoL",
                "Use",
                "Maintenance",
            ]
        )
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
        num_rows = 1
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
        num_cars = len(self.carData)
        self.setRowCount(num_cars)
        for row in range(num_cars):
            carIndex = row
            self.set_table_item(
                row,
                0,
                f"Car {carIndex}" if carIndex != 0 else "Current",
                self.itemFontBig,
            )
            self.set_table_item(
                row,
                1,
                f"{self.carData[carIndex]['carSegment']} - {self.carData[carIndex]['engineType']}",
            )
            self.set_table_item(
                row, 2, f"{self.carData[carIndex]['DeltaTHco2']:.1f}", self.itemFontBig
            )
            if row != 0:
                self.carData[carIndex]["co2Savings"] = (
                    self.carData[0]["THco2"] - self.carData[carIndex]["THco2"]
                )
                self.set_table_item(
                    row,
                    3,
                    f"{self.carData[carIndex]['co2Savings']:.1f}",
                    self.itemFontBig,
                )
            else:
                self.carData[carIndex]["co2Savings"] = None
                self.set_table_item(row, 3, "/", self.itemFontBig)
            self.set_table_item(
                row, 4, f"{self.carData[carIndex]['yearlyCo2']:.2f}", self.itemFontBig
            )
            prod = self.carData[carIndex]["relativeProductionCo2"]
            eol = self.carData[carIndex]["relativeEolCo2"]
            use = self.carData[carIndex]["relativeUseCo2"]
            mnt = self.carData[carIndex]["relativeMaintenanceCo2"]
            prod_r = round(prod, 1)
            eol_r = round(eol, 1)
            use_r = round(use, 1)
            if self.parent.generalSettings["maintenance"]:
                mnt_r = round(100.0 - (prod_r + eol_r + use_r), 1)
            elif self.carData[carIndex]["engineType"] == "BEV" and mnt != 0:
                mnt_r = round(100.0 - (prod_r + eol_r + use_r), 1)
            else:
                mnt_r = None
                use_r = round(100.0 - (prod_r + eol_r), 1)
            self.carData[carIndex]["relativeProductionCo2"] = prod_r
            self.carData[carIndex]["relativeEolCo2"] = eol_r
            self.carData[carIndex]["relativeUseCo2"] = use_r
            self.carData[carIndex]["relativeMaintenanceCo2"] = mnt_r
            self.set_table_item(row, 5, f"{prod_r:.1f} %", self.itemFontBig)
            self.set_table_item(row, 6, f"{eol_r:.1f} %", self.itemFontBig)
            self.set_table_item(row, 7, f"{use_r:.1f} %", self.itemFontBig)
            if mnt_r is not None:
                self.set_table_item(row, 8, f"{mnt_r:.1f} %", self.itemFontBig)
            else:
                self.set_table_item(row, 8, "/", self.itemFontBig)

    def set_table_item(self, row, col, text, font=None):
        item = QTableWidgetItem(text)
        if font:
            item.setFont(font)
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)
