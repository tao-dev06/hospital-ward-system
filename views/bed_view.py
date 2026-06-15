# views/bed_view.py
# 病床监控界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QPushButton, QLabel, QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from models.bed import BedModel
from models.ward import WardModel
from utils.helpers import (
    populate_table, get_selected_row_data, set_form_data,
    clear_form, get_form_data, show_info, show_error, confirm
)


class BedView(QWidget):
    """病床监控页面"""

    COLUMNS = [
        ("编号", "bed_id"),
        ("床位号", "bed_no"),
        ("病房", "ward_name"),
        ("科室", "dept_name"),
        ("状态", "status"),
        ("类型", "bed_type"),
    ]

    STATUS_COLUMNS = [
        ("科室", "dept_name"),
        ("病房", "ward_name"),
        ("类型", "ward_type"),
        ("床号", "bed_no"),
        ("床位类型", "bed_type"),
        ("状态", "bed_status"),
        ("占用患者", "occupied_by"),
        ("入住时间", "occupy_since"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("🛏️ 病床监控")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 视图切换
        tab_layout = QHBoxLayout()
        self.btn_mgmt = QPushButton("病床管理")
        self.btn_status = QPushButton("状态总览")
        self.btn_mgmt.setStyleSheet(
            "background: #3498db; color: white; padding: 8px 20px; "
            "border-radius: 4px; font-size: 14px; border: none;")
        self.btn_status.setStyleSheet(
            "background: #bdc3c7; color: white; padding: 8px 20px; "
            "border-radius: 4px; font-size: 14px; border: none;")
        self.btn_mgmt.clicked.connect(lambda: self._switch_tab(0))
        self.btn_status.clicked.connect(lambda: self._switch_tab(1))
        tab_layout.addWidget(self.btn_mgmt)
        tab_layout.addWidget(self.btn_status)
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # ===== 病床管理 Tab =====
        self.mgmt_tab = QWidget()
        mt_layout = QVBoxLayout(self.mgmt_tab)

        # 搜索
        sl = QHBoxLayout()
        sl.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按床位号/病房搜索...")
        sl.addWidget(self.search_input)
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self._load_data)
        sl.addWidget(self.btn_refresh)
        sl.addStretch()
        mt_layout.addLayout(sl)

        # 表单
        fg = QGroupBox("病床信息")
        fl = QVBoxLayout(fg)
        row = QHBoxLayout()

        self.widgets = {}

        self.widgets["bed_no"] = QLineEdit()
        row.addWidget(QLabel("床位号:"))
        row.addWidget(self.widgets["bed_no"])

        self.widgets["ward_id"] = QComboBox()
        row.addWidget(QLabel("病房:"))
        row.addWidget(self.widgets["ward_id"])

        self.widgets["status"] = QComboBox()
        self.widgets["status"].addItems(["空闲", "已占用", "清洁中", "维修中"])
        row.addWidget(QLabel("状态:"))
        row.addWidget(self.widgets["status"])

        self.widgets["bed_type"] = QComboBox()
        self.widgets["bed_type"].addItems(["普通床", "升降床", "ICU床"])
        row.addWidget(QLabel("类型:"))
        row.addWidget(self.widgets["bed_type"])

        fl.addLayout(row)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("➕ 新增")
        self.btn_edit = QPushButton("✏️ 修改")
        self.btn_delete = QPushButton("🗑️ 删除")
        self.btn_clear = QPushButton("🧹 清空")
        for btn in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_clear]:
            btn.setStyleSheet("padding: 8px 16px; font-size: 13px;")
            btn_row.addWidget(btn)
        btn_row.addStretch()

        self.btn_add.clicked.connect(self._add)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_delete.clicked.connect(self._delete)
        self.btn_clear.clicked.connect(lambda: clear_form(self.widgets))
        fl.addLayout(btn_row)
        mt_layout.addWidget(fg)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self._on_select)
        mt_layout.addWidget(self.table, 1)

        layout.addWidget(self.mgmt_tab, 1)

        # ===== 状态总览 Tab =====
        self.status_tab = QWidget()
        st_layout = QVBoxLayout(self.status_tab)

        # 过滤器
        flt = QHBoxLayout()
        flt.addWidget(QLabel("按状态筛选:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "空闲", "已占用", "清洁中", "维修中"])
        self.status_filter.currentIndexChanged.connect(self._filter_status)
        flt.addWidget(self.status_filter)
        flt.addStretch()

        self.btn_sync = QPushButton("🔄 同步状态")
        self.btn_sync.clicked.connect(self._load_status)
        flt.addWidget(self.btn_sync)
        st_layout.addLayout(flt)

        self.status_table = QTableWidget()
        self.status_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.status_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.status_table.setAlternatingRowColors(True)
        st_layout.addWidget(self.status_table, 1)

        layout.addWidget(self.status_tab, 1)

        # 默认显示管理
        self.status_tab.hide()
        self._current_tab = 0

        # 加载病房列表
        self._load_wards()

    def _switch_tab(self, tab):
        self._current_tab = tab
        if tab == 0:
            self.mgmt_tab.show()
            self.status_tab.hide()
            self.btn_mgmt.setStyleSheet(
                "background: #3498db; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self.btn_status.setStyleSheet(
                "background: #bdc3c7; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self._load_data()
        else:
            self.mgmt_tab.hide()
            self.status_tab.show()
            self.btn_status.setStyleSheet(
                "background: #3498db; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self.btn_mgmt.setStyleSheet(
                "background: #bdc3c7; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self._load_status()

    def _load_wards(self):
        try:
            wards = WardModel.get_all()
            self._ward_map = {w["ward_name"]: w["ward_id"] for w in wards}
            self.widgets["ward_id"].clear()
            self.widgets["ward_id"].addItems(self._ward_map.keys())
        except Exception as e:
            show_error("错误", f"加载病房失败: {e}")

    def _load_data(self):
        try:
            data = BedModel.get_all()
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载病床数据失败: {e}")

    def _on_select(self):
        data = get_selected_row_data(self.table, self.COLUMNS)
        if data:
            ward_name = data.get("ward_name", "")
            data["ward_id"] = ward_name
            set_form_data(self.widgets, data)

    def _add(self):
        data = get_form_data(self.widgets)
        if not data.get("bed_no"):
            show_error("错误", "床位号不能为空！")
            return
        data["ward_id"] = self._ward_map.get(data["ward_id"], data["ward_id"])
        if not data["ward_id"]:
            show_error("错误", "请选择病房！")
            return
        try:
            BedModel.insert(data)
            show_info("成功", "病床添加成功！")
            clear_form(self.widgets)
            self._load_data()
        except Exception as e:
            show_error("错误", f"添加失败: {e}")

    def _edit(self):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        data = get_form_data(self.widgets)
        data["bed_id"] = selected["bed_id"]
        data["ward_id"] = self._ward_map.get(data["ward_id"], data["ward_id"])
        try:
            BedModel.update(data)
            show_info("成功", "病床修改成功！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"修改失败: {e}")

    def _delete(self):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        if not confirm("确认删除", f"确定要删除病床 [{selected['ward_name']} {selected['bed_no']}] 吗？"):
            return
        try:
            BedModel.delete(selected["bed_id"])
            show_info("成功", "删除成功！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"删除失败: {e}")

    def _load_status(self):
        try:
            data = BedModel.bed_status_view()
            self._status_data = data
            self._filter_status()
        except Exception as e:
            show_error("错误", f"加载状态失败: {e}")

    def _filter_status(self):
        filter_text = self.status_filter.currentText()
        data = self._status_data if hasattr(self, "_status_data") else []
        if filter_text != "全部":
            data = [d for d in data if d.get("bed_status") == filter_text]

        # 自定义表格，带颜色标记
        self.status_table.setRowCount(len(data))
        self.status_table.setColumnCount(len(self.STATUS_COLUMNS))
        headers = [c[0] for c in self.STATUS_COLUMNS]
        self.status_table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_def in enumerate(self.STATUS_COLUMNS):
                key = col_def[1]
                value = row_data.get(key, "") or ""
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                # 颜色标记
                status = row_data.get("bed_status", "")
                if status == "已占用":
                    item.setBackground(QColor("#ffcccc"))  # 红色
                elif status == "空闲":
                    item.setBackground(QColor("#ccffcc"))  # 绿色
                elif status == "清洁中":
                    item.setBackground(QColor("#ffffcc"))  # 黄色
                elif status == "维修中":
                    item.setBackground(QColor("#cccccc"))  # 灰色

                self.status_table.setItem(row_idx, col_idx, item)

        self.status_table.resizeColumnsToContents()
