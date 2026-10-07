"""Small helpers for Qt form layouts."""


def set_layout_visible(layout, visible):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.setVisible(visible)
        layout.invalidate()
    parent_widget = layout.parentWidget()
    if parent_widget:
        parent_widget.adjustSize()
