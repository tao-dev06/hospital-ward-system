# utils/helpers.py
# GUI 工具函数
from PyQt5.QtWidgets import (
    QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit,
    QTableWidget
)
from PyQt5.QtCore import QDate, Qt


def show_info(title, message):
    """显示信息对话框"""
    QMessageBox.information(None, title, str(message))


def show_warning(title, message):
    """显示警告对话框"""
    QMessageBox.warning(None, title, str(message))


def show_error(title, message):
    """显示错误对话框"""
    QMessageBox.critical(None, title, str(message))


def confirm(title, message):
    """确认对话框，返回 True/False"""
    reply = QMessageBox.question(
        None, title, str(message),
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


def populate_table(table: QTableWidget, data, columns, stretch_last=True):
    """将数据填充到 QTableWidget"""
    if not data:
        table.setRowCount(0)
        return

    table.setRowCount(len(data))
    table.setColumnCount(len(columns))

    # 设置表头
    headers = [col[0] for col in columns]
    table.setHorizontalHeaderLabels(headers)

    # 填充数据
    for row_idx, row_data in enumerate(data):
        for col_idx, col_def in enumerate(columns):
            key = col_def[1]
            value = row_data.get(key, "")
            if value is None:
                value = ""
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, col_idx, item)

    # 优化表格显示
    table.resizeColumnsToContents()
    if stretch_last:
        header = table.horizontalHeader()
        header.setStretchLastSection(True)


def get_selected_row_data(table, columns):
    """获取表格选中行的数据"""
    row = table.currentRow()
    if row < 0:
        return None
    data = {}
    for col_idx, col_def in enumerate(columns):
        key = col_def[1]
        item = table.item(row, col_idx)
        data[key] = item.text() if item else ""
    return data


def set_form_data(form_widgets, data):
    """将数据填充到表单控件"""
    for field, widget in form_widgets.items():
        if field not in data or data[field] is None:
            continue
        value = data[field]
        w = widget
        if isinstance(w, QLineEdit):
            w.setText(str(value))
        elif isinstance(w, QComboBox):
            idx = w.findText(str(value))
            if idx >= 0:
                w.setCurrentIndex(idx)
        elif isinstance(w, QDateEdit):
            if isinstance(value, str) and value:
                w.setDate(QDate.fromString(value[:10], "yyyy-MM-dd"))
        elif isinstance(w, QSpinBox):
            w.setValue(int(value) if value else 0)
        elif isinstance(w, QDoubleSpinBox):
            w.setValue(float(value) if value else 0.0)
        elif isinstance(w, QTextEdit):
            w.setPlainText(str(value))


def clear_form(form_widgets):
    """清空表单控件"""
    for widget in form_widgets.values():
        w = widget
        if isinstance(w, QLineEdit):
            w.clear()
        elif isinstance(w, QComboBox):
            w.setCurrentIndex(0)
        elif isinstance(w, QDateEdit):
            w.setDate(QDate.currentDate())
        elif isinstance(w, QSpinBox):
            w.setValue(0)
        elif isinstance(w, QDoubleSpinBox):
            w.setValue(0.0)
        elif isinstance(w, QTextEdit):
            w.clear()


def get_form_data(form_widgets):
    """从表单控件获取数据"""
    data = {}
    for field, widget in form_widgets.items():
        w = widget
        if isinstance(w, QLineEdit):
            data[field] = w.text().strip()
        elif isinstance(w, QComboBox):
            data[field] = w.currentText()
        elif isinstance(w, QDateEdit):
            data[field] = w.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        elif isinstance(w, QSpinBox):
            data[field] = w.value()
        elif isinstance(w, QDoubleSpinBox):
            data[field] = w.value()
        elif isinstance(w, QTextEdit):
            data[field] = w.toPlainText().strip()
    return data
