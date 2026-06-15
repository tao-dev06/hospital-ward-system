# views/ward_view.py
# 病房管理界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QFormLayout, QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.ward import WardModel
from models.department import DepartmentModel
from utils.helpers import (
    populate_table, get_selected_row_data, set_form_data,
    clear_form, get_form_data, show_info, show_error, confirm
)


class WardView(QWidget):
    """病房管理页面"""

    COLUMNS = [
        ("编号", "ward_id"),
        ("病房名称", "ward_name"),
        ("所属科室", "dept_name"),
        ("病房类型", "ward_type"),
        ("床位数", "capacity"),
        ("日床位费", "price_per_day"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("🏠 病房管理")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按病房名称或科室搜索...")
        self.search_input.setMinimumWidth(250)
        self.search_input.returnPressed.connect(self._search)
        search_layout.addWidget(self.search_input)
        self.btn_search = QPushButton("🔍 搜索")
        self.btn_search.clicked.connect(self._search)
        search_layout.addWidget(self.btn_search)
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self._load_data)
        search_layout.addWidget(self.btn_refresh)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 表单区
        form_group = QGroupBox("病房信息表单")
        fl = QFormLayout(form_group)

        self.widgets = {}

        self.widgets["ward_name"] = QLineEdit()
        fl.addRow("病房名称*:", self.widgets["ward_name"])

        self.widgets["dept_id"] = QComboBox()
        fl.addRow("所属科室*:", self.widgets["dept_id"])

        self.widgets["ward_type"] = QComboBox()
        self.widgets["ward_type"].addItems(["普通病房", "ICU", "特需病房", "隔离病房"])
        fl.addRow("病房类型:", self.widgets["ward_type"])

        self.widgets["capacity"] = QSpinBox()
        self.widgets["capacity"].setRange(1, 20)
        self.widgets["capacity"].setValue(4)
        fl.addRow("床位数:", self.widgets["capacity"])

        self.widgets["price_per_day"] = QDoubleSpinBox()
        self.widgets["price_per_day"].setRange(0, 99999.99)
        self.widgets["price_per_day"].setDecimals(2)
        self.widgets["price_per_day"].setValue(150.00)
        fl.addRow("日床位费(元):", self.widgets["price_per_day"])

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ 新增")
        self.btn_edit = QPushButton("✏️ 修改")
        self.btn_delete = QPushButton("🗑️ 删除")
        self.btn_clear = QPushButton("🧹 清空")
        for btn in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_clear]:
            btn.setStyleSheet("padding: 8px 16px; font-size: 13px;")
            btn_layout.addWidget(btn)
        btn_layout.addStretch()

        self.btn_add.clicked.connect(self._add)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_delete.clicked.connect(self._delete)
        self.btn_clear.clicked.connect(lambda: clear_form(self.widgets))
        fl.addRow(btn_layout)

        layout.addWidget(form_group)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self._on_select)
        layout.addWidget(self.table, 1)

        # 加载科室到下拉框
        self._load_depts()

    def _load_depts(self):
        try:
            depts = DepartmentModel.get_all()
            self._dept_map = {d["dept_name"]: d["dept_id"] for d in depts}
            self.widgets["dept_id"].clear()
            self.widgets["dept_id"].addItems(self._dept_map.keys())
        except Exception as e:
            show_error("错误", f"加载科室失败: {e}")

    def _load_data(self):
        try:
            data = WardModel.get_all()
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载病房数据失败: {e}")

    def _search(self):
        kw = self.search_input.text().strip()
        if not kw:
            self._load_data()
            return
        try:
            data = WardModel.search(kw)
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _on_select(self):
        data = get_selected_row_data(self.table, self.COLUMNS)
        if data:
            # 将 dept_name 映射到 dept_id
            dept_name = data.get("dept_name", "")
            dept_id = self._dept_map.get(dept_name)
            data["dept_id"] = dept_id
            set_form_data(self.widgets, data)

    def _add(self):
        data = get_form_data(self.widgets)
        if not data.get("ward_name"):
            show_error("错误", "病房名称不能为空！")
            return
        # 将科室名称转 ID
        data["dept_id"] = self._dept_map.get(data["dept_id"], data["dept_id"])
        try:
            WardModel.insert(data)
            show_info("成功", "病房添加成功！")
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
        data["ward_id"] = selected["ward_id"]
        data["dept_id"] = self._dept_map.get(data["dept_id"], data["dept_id"])
        if not data.get("ward_name"):
            show_error("错误", "病房名称不能为空！")
            return
        try:
            WardModel.update(data)
            show_info("成功", "病房修改成功！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"修改失败: {e}")

    def _delete(self):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        if not confirm("确认删除", f"确定要删除病房 [{selected['ward_name']}] 吗？"):
            return
        try:
            WardModel.delete(selected["ward_id"])
            show_info("成功", "删除成功！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"删除失败（可能有关联病床）: {e}")
