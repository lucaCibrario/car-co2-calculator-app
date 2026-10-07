from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.replacement_options import OptionsDialog
from eco_car_advisor.ui.widgets.stored_combo_box import StoredComboBox


class Car(QWidget):
    def __init__(self, carSegments, carEngineTypes, parent=None):
        super().__init__()
        self.parent = parent
        self.data = parent.data
        self.tooltip_dict = parent.tooltip_dict
        self.carSegments = carSegments
        self.carEngineTypes = carEngineTypes
        self.carLayout = QVBoxLayout()
        self.carLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.carLayout)
        self.input_group = QGroupBox()
        self.firstLineLayout = QHBoxLayout()
        carNumber = len(self.parent.cars) + 1 if self.parent.cars else 1
        self.carNumber_label = QLabel(f"Car {carNumber}:")
        self.carNumber_label.setFixedWidth(45)
        self.segments_comboBox = StoredComboBox("carSegment", self.carSegments)
        self.engineType_comboBox = StoredComboBox("engineType", self.carEngineTypes, defaultIndex=2)
        self.optionsButton = QPushButton()
        self.optionsButton.setIcon(QIcon(resource_path("Icons/Options.png")))
        self.optionsButton.setToolTip("Click for more setting parameters.")
        self.optionsButton.setFixedSize(32, 32)
        self.optionsButton.clicked.connect(self.open_options_dialog)
        self.optionsLabel = QLabel("Configure Car")
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon(resource_path("Icons/Minus.png")))
        self.remove_button.setToolTip("Click to remove the car from the analysis.")
        self.remove_button.setFixedSize(32, 32)
        self.remove_button.clicked.connect(self.remove_car)
        self.firstLineLayout.addWidget(self.carNumber_label)
        self.firstLineLayout.addWidget(self.segments_comboBox)
        self.firstLineLayout.addWidget(self.engineType_comboBox)
        self.firstLineLayout.addWidget(self.optionsButton)
        self.firstLineLayout.addWidget(self.remove_button)
        self.input_group.setLayout(self.firstLineLayout)
        self.carLayout.addWidget(self.input_group)
        self.dialog = OptionsDialog(self)
        self.segments_comboBox.setToolTip(self.tooltip_dict["carSegment"])
        self.engineType_comboBox.setToolTip(self.tooltip_dict["engineType"])

    def open_options_dialog(self):
        """Opens the options window."""
        if self.dialog.exec(self.segments_comboBox.read(), self.engineType_comboBox.read()):
            self.segments_comboBox.write(self.dialog.segments_comboBox.read())
            self.engineType_comboBox.write(self.dialog.engineType_comboBox.read())

    def remove_car(self):
        """Remove a specific car input section."""
        if self.parent:
            self.parent.remove_car(self)
        self.close()
        self.parent.renumber_cars()

    def read(self):
        """Extracts the current data from the Car widget."""
        self.dialog.segments_comboBox.write(self.segments_comboBox.read())
        self.dialog.engineType_comboBox.write(self.engineType_comboBox.read())
        if self.dialog.has_changes():
            self.dialog.set_default_values()
            self.dialog.state()
        exportData = self.dialog.current_state.copy()
        return exportData
