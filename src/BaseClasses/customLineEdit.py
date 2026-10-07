# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 07:52:18 2025

@author: lucac
"""

from PySide6.QtWidgets import QLineEdit, QMessageBox
from PySide6.QtCore import Signal
from typing import Union


class myQLineEdit(QLineEdit):
    valueChanged = Signal(str)

    def __init__(self,
                 variableLabel: str = '',
                 text: Union[str, float] = "",
                 placeHolderText: str = "",
                 validateLabel: str = "",
                 compulsory=True,
                 allowNegative=False,
                 upperLimit: float = None,
                 parent=None):

        super().__init__(parent)

        self._variableLabel = variableLabel
        self._text = str(text)
        self._defaultValue = self._text
        self._storedValue = self._text
        self._previousValue = self._text
        self._validateLabel = validateLabel or variableLabel
        self._compulsory = compulsory
        self._allowNegative = allowNegative
        self._upperLimit = upperLimit

        self.editingFinished.connect(self._on_editing_finished)

        self.write(self._text)
        if placeHolderText:
            self.setPlaceholderText(placeHolderText)

        if not text or not self.validate_numeric_input():
            self.save()

    def save(self):
        value = self.read()
        self._storedValue = value
        self._previousValue = value
        return self.state()

    def _on_editing_finished(self):
        if self.validate_numeric_input_onTheFly() is None:  # No error = valid input
            value = self.read()
            self._previousValue = value
            self.valueChanged.emit(value)

    def reset_to_default(self):
        self.write(self._defaultValue)
        self._previousValue = self._defaultValue

    def restore_storedValue(self):
        self.write(self._storedValue)

    def write(self, value: Union[str, float], save: bool = False):
        self.setText(str(value))
        self._previousValue = str(value)
        if save:
            if not self.validate_numeric_input():
                self.save()

    def read(self) -> str:
        return self.text()

    def state(self, returnType=float) -> dict:
        if self._variableLabel:
            value = self.read()
            if value:
                if returnType == float:
                    return {self._variableLabel: float(value)}
                elif returnType == str:
                    return {self._variableLabel: str(value)}
            else:
                return {self._variableLabel: None}

    def validate_numeric_input(self, errorPanel=True) -> str | None:
        """Validates if current text is numeric and shows warning if invalid."""
        text = self.read().strip()

        if not text:
            if self._compulsory:
                self.write(self._previousValue)
                return self._show_error(f"{self._validateLabel} cannot be empty.", errorPanel)
            return None

        try:
            value = float(text)
        except ValueError:
            self.write(self._previousValue)
            return self._show_error(f"Enter a valid numeric value for {self._validateLabel}.", errorPanel)

        if not self._allowNegative and value < 0:
            self.write(self._previousValue)
            return self._show_error(f"Enter a positive numeric value for {self._validateLabel}.", errorPanel)

        if self._upperLimit:
            if value > self._upperLimit:
                self.write(self._previousValue)
                return self._show_error(f"Enter a numeric value lower than {self._upperLimit}.", errorPanel)

        return None  # Input is valid

    def validate_numeric_input_onTheFly(self) -> str | None:
        """Validates if current text is numeric and shows warning if invalid."""
        text = self.read().strip()

        if not text:
            return None

        try:
            value = float(text)
        except ValueError:
            self.write(self._previousValue)
            return self._show_error(f"Enter a valid numeric value for {self._validateLabel}.")

        if not self._allowNegative and value < 0:
            self.write(self._previousValue)
            return self._show_error(f"Enter a positive numeric value for {self._validateLabel}.")

        if self._upperLimit:
            if value > self._upperLimit:
                self.write(self._previousValue)
                return self._show_error(f"Enter a numeric value lower than {self._upperLimit}.")

        return None  # Input is valid

    def _show_error(self, message: str, errorPanel: bool = True) -> str:
        if errorPanel:
            QMessageBox.warning(self, "Invalid Input", message)
        return message

    def set_compulsory(self, state: bool):
        self._compulsory = state

    def set_allowNegative(self, state: bool):
        self._allowNegative = state

    def update_default_value(self, value):
        self._defaultValue = value

    def update_stored_value(self, value):
        self._previousValue = value
