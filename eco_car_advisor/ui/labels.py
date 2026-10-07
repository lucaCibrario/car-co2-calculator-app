"""Small reusable labels for the application window."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel


class ConfidentialLabel(QLabel):
    """Display the application's current restricted-use notice."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Arial", 12, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel { color: red; border: 2px solid red; padding: 7px; background-color: white; }"
        )
