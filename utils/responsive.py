# utils/responsive.py
import re

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QDoubleSpinBox, QGroupBox,
    QHeaderView, QLabel, QLayout, QLineEdit, QListWidget, QPushButton,
    QSpinBox, QTableWidget, QTextEdit, QWidget
)


class ResponsiveScaler:
    """Scale fonts, spacing, and common widget sizes from their original values."""

    PX_PATTERN = re.compile(r"(?<!#)\b(\d+(?:\.\d+)?)px\b")

    def __init__(self, root, base_size=(1200, 750), min_scale=0.75, max_scale=1.6):
        self.root = root
        self.base_width, self.base_height = base_size
        self.min_scale = min_scale
        self.max_scale = max_scale
        self._widget_state = {}
        self._layout_state = {}

    def apply(self):
        scale = self._current_scale()
        self._scale_widget_tree(self.root, scale)

    def _current_scale(self):
        width_scale = self.root.width() / self.base_width
        height_scale = self.root.height() / self.base_height
        return max(self.min_scale, min(width_scale, height_scale, self.max_scale))

    def _scaled(self, value, scale, minimum=1):
        return max(minimum, int(round(value * scale)))

    def _scale_widget_tree(self, widget, scale):
        if not isinstance(widget, QWidget):
            return

        self._scale_widget(widget, scale)
        self._scale_layout_tree(widget.layout(), scale)
        for child in widget.findChildren(QWidget):
            self._scale_widget(child, scale)
            self._scale_layout_tree(child.layout(), scale)

    def _scale_layout_tree(self, layout, scale):
        if layout is None:
            return

        state = self._layout_state.setdefault(
            id(layout),
            {
                "spacing": layout.spacing(),
                "margins": layout.getContentsMargins(),
            },
        )
        if state["spacing"] >= 0:
            layout.setSpacing(self._scaled(state["spacing"], scale, 0))

        left, top, right, bottom = state["margins"]
        layout.setContentsMargins(
            self._scaled(left, scale, 0),
            self._scaled(top, scale, 0),
            self._scaled(right, scale, 0),
            self._scaled(bottom, scale, 0),
        )

        for i in range(layout.count()):
            item = layout.itemAt(i)
            child_layout = item.layout()
            if isinstance(child_layout, QLayout):
                self._scale_layout_tree(child_layout, scale)

    def _scale_widget(self, widget, scale):
        state = self._widget_state.setdefault(id(widget), self._capture_widget_state(widget))

        font = QFont(state["font"])
        if state["font_size"] > 0:
            font.setPointSize(max(7, self._scaled(state["font_size"], scale)))
            widget.setFont(font)

        if state["style"]:
            widget.setStyleSheet(self._scale_style_sheet(state["style"], scale))

        if state["minimum_width"] > 0:
            widget.setMinimumWidth(self._scaled(state["minimum_width"], scale))
        if state["minimum_height"] > 0:
            widget.setMinimumHeight(self._scaled(state["minimum_height"], scale))
        if 0 < state["maximum_height"] < 16777215:
            widget.setMaximumHeight(self._scaled(state["maximum_height"], scale))

        if isinstance(widget, (QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox)):
            widget.setMinimumHeight(self._scaled(34, scale, 26))
        elif isinstance(widget, QPushButton):
            widget.setMinimumHeight(self._scaled(36, scale, 28))
        elif isinstance(widget, QTextEdit):
            widget.setMinimumHeight(self._scaled(70, scale, 48))
        elif isinstance(widget, QListWidget):
            widget.setFixedWidth(self._scaled(160, scale, 120))
            widget.setIconSize(QSize(self._scaled(22, scale), self._scaled(22, scale)))
        elif isinstance(widget, QTableWidget):
            self._scale_table(widget, scale)
        elif isinstance(widget, QAbstractItemView):
            widget.setIconSize(QSize(self._scaled(20, scale), self._scaled(20, scale)))
        elif isinstance(widget, QLabel):
            widget.setWordWrap(True)

        widget.updateGeometry()

    def _capture_widget_state(self, widget):
        return {
            "font": QFont(widget.font()),
            "font_size": widget.font().pointSize(),
            "style": widget.styleSheet(),
            "minimum_width": widget.minimumWidth(),
            "minimum_height": widget.minimumHeight(),
            "maximum_height": widget.maximumHeight(),
        }

    def _scale_style_sheet(self, style_sheet, scale):
        def repl(match):
            value = float(match.group(1))
            scaled = self._scaled(value, scale, 0)
            return f"{scaled}px"

        return self.PX_PATTERN.sub(repl, style_sheet)

    def _scale_table(self, table, scale):
        table.verticalHeader().setDefaultSectionSize(self._scaled(34, scale, 24))
        table.horizontalHeader().setMinimumSectionSize(self._scaled(60, scale, 42))
        table.setIconSize(QSize(self._scaled(20, scale), self._scaled(20, scale)))

        header_font = QFont(table.horizontalHeader().font())
        base_size = self._widget_state.get(id(table), {}).get("font_size", 13)
        header_font.setPointSize(max(7, self._scaled(base_size, scale)))
        table.horizontalHeader().setFont(header_font)

        for header in (table.horizontalHeader(), table.verticalHeader()):
            header.setSectionResizeMode(QHeaderView.Interactive)
            header.setStretchLastSection(True)
