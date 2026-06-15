# views/nurse_view.py
# 护士管理界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QPushButton, QLabel,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.nurse import NurseModel
from models.department import DepartmentModel
from utils.helpers import (
    populate_table, get_selected_row_data, set_form_data,
    clear_form, get_form_data, show_info, show_error, confirm
)


class NurseView(QWidget):
    """护士管理页面"""

    COLUMNS = [
        ("编号", "nurse_id"),
        ("姓名", "name"),
        ("性别", "gender"),
        ("科室", "dept_name"),
        ("联系电话", "phone"),
        ("班次", "shift"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("👩‍⚕️ 护士管理")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 搜索
        sl = QHBoxLayout()
        sl.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按姓名/科室搜索...")
        self.search_input.setMinimumWidth(250)
        self.search_input.returnPressed.connect(self._search)
        sl.addWidget(self.search_input)
        self.btn_search = QPushButton("🔍 搜索")
        self.btn_search.clicked.connect(self._search)
        sl.addWidget(self.btn_search)
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self._load_data)
        sl.addWidget(self.btn_refresh)
        sl.addStretch()
        layout.addLayout(sl)

        # 表单
        fg = QGroupBox("护士信息表单")
        fl = QVBoxLayout(fg)
        row = QHBoxLayout()

        self.widgets = {}

        self.widgets["name"] = QLineEdit()
        row.addWidget(QLabel("姓名*:"))
        row.addWidget(self.widgets["name"])

        self.widgets["gender"] = QComboBox()
        self.widgets["gender"].addItems(["女", "男"])
        row.addWidget(QLabel("性别:"))
        row.addWidget(self.widgets["gender"])

        self.widgets["dept_id"] = QComboBox()
        row.addWidget(QLabel("科室:"))
        row.addWidget(self.widgets["dept_id"])

        self.widgets["phone"] = QLineEdit()
        row.addWidget(QLabel("电话:"))
        row.addWidget(self.widgets["phone"])

        self.widgets["shift"] = QComboBox()
        self.widgets["shift"].addItems(["白班", "夜班", "中班"])
        row.addWidget(QLabel("班次:"))
        row.addWidget(self.widgets["shift"])

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
        layout.addWidget(fg)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self._on_select)
        layout.addWidget(self.table, 1)

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
            data = NurseModel.get_all()
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载护士数据失败: {e}")

    def _search(self):
        kw = self.search_input.text().strip()
        if not kw:
            self._load_data()
            return
        try:
            data = NurseModel.search(kw)
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _on_select(self):
        data = get_selected_row_data(self.table, self.COLUMNS)
        if data:
            dept_name = data.get("dept_name", "")
            data["dept_id"] = dept_name
            set_form_data(self.widgets, data)

    def _add(self):
        data = get_form_data(self.widgets)
        if not data["name"]:
            show_error("错误", "姓名不能为空！")
            return
        data["dept_id"] = self._dept_map.get(data["dept_id"], data["dept_id"])
        try:
            NurseModel.insert(data)
            show_info("成功", "护士添加成功！")
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
        data["nurse_id"] = selected["nurse_id"]
        data["dept_id"] = self._dept_map.get(data["dept_id"], data["dept_id"])
        try:
            NurseModel.update(data)
            show_info("成功", "护士信息修改成功！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"修改失败: {e}")

    def _delete(self):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        if not confirm("确认删除", f"确定要删除护士 [{selected['name']}] 吗？"):
            return
        try:
            NurseModel.delete(selected["nurse_id"])
            show_info("成功", "删除成功！")
            clear_form(self.widgets)
            self._load_data()
        except Exception as e:
            show_error("错误", f"删除失败: {e}")
