"""Start the ECO Car Replacement Advisor desktop application."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from eco_car_advisor.resources import resource_path
from eco_car_advisor.ui.main_window import CarReplacementAdvisor


def main() -> int:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path("Icons/TitleIcon.ico"))))
    app.setStyle("windows10")
    window = CarReplacementAdvisor()
    window.setWindowIcon(QIcon(str(resource_path("Icons/TitleIcon.ico"))))
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
