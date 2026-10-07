"""Combo box with a restorable saved value."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox


class StoredComboBox(QComboBox):
    valueChanged = Signal(str)

    def __init__(
        self,
        variableLabel: str = "",
        items: list[str] | None = None,
        defaultIndex: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self._variableLabel = variableLabel
        items = items if items is not None else []
        self._items = items
        self._defaultValue = defaultIndex
        self.addItems(items)
        self.write(defaultIndex)
        self.currentTextChanged.connect(self._on_text_changed)
        self.save()

    def _on_text_changed(self, text):
        self.valueChanged.emit(text)

    def reset_to_default(self):
        self.write(self._defaultValue)

    def restore_storedValue(self):
        self.write(self._previousValue)

    def write(self, value: str | int, save: bool = False):
        if isinstance(value, str):
            index = self.findText(value)
            if index >= 0:
                self.setCurrentIndex(index)
                if save:
                    self.save()
            else:
                print(f"[StoredComboBox] Warning: item '{value}' not found.")
        elif isinstance(value, int):
            if 0 <= value < self.count():
                self.setCurrentIndex(value)
                if save:
                    self.save()
            else:
                print(f"[StoredComboBox] Warning: index {value} out of range.")
        else:
            print(f"[StoredComboBox] Warning: unsupported type {type(value)} for write().")

    def read(self) -> str:
        return self.currentText()

    def save(self):
        self._previousValue = self.read()
        return self.state()

    def state(self) -> dict:
        if self._variableLabel:
            return {self._variableLabel: str(self.read())}
