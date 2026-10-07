"""
Custom QCheckBox with state tracking and interface consistency.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox


class StoredCheckBox(QCheckBox):
    valueChanged = Signal(bool)

    def __init__(
        self,
        variableLabel: str = "",
        text: str = "",
        defaultValue: bool = False,
        parent=None,
    ):
        super().__init__(text, parent)
        self._variableLabel = variableLabel
        self._defaultValue = defaultValue
        self.write(defaultValue)
        self.stateChanged.connect(self._on_state_changed)
        self.save()

    def _on_state_changed(self, state: int):
        """Emit signal when checkbox state changes (converted to bool)."""
        self.valueChanged.emit(bool(state))

    def write(self, value, save: bool = False):
        """Set checkbox state using bool or int (0/1)."""
        if isinstance(value, (bool, int)):
            self.setChecked(bool(value))
            if save:
                self.save()
        else:
            print(f"[StoredCheckBox] Warning: write() expects bool or int, got {type(value)}")

    def read(self) -> bool:
        return self.isChecked()

    def reset_to_default(self):
        self.setChecked(self._defaultValue)

    def restore_storedValue(self):
        self.setChecked(self._previousValue)

    def save(self):
        self._previousValue = self.read()
        return self.state()

    def state(self) -> dict:
        if self._variableLabel:
            return {self._variableLabel: bool(self.read())}
