# views/order_view.py
# 医嘱管理界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit, QPushButton, QLabel,
    QDialog, QDialogButtonBox, QFormLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.medical_order import MedicalOrderModel
from models.inpatient import InpatientModel
from models.doctor import DoctorModel
from models.nurse import NurseModel
from utils.helpers import (
    populate_table, get_selected_row_data, set_form_data,
    clear_form, get_form_data, show_info, show_error, confirm
)


class OrderView(QWidget):
    """医嘱管理页面"""

    COLUMNS = [
        ("编号", "order_id"),
        ("患者", "patient_name"),
        ("病房", "ward_name"),
        ("床号", "bed_no"),
        ("类型", "order_type"),
        ("内容", "order_content"),
        ("用量", "dosage"),
        ("开嘱医生", "doctor_name"),
        ("执行护士", "nurse_name"),
        ("状态", "status"),
        ("费用(元)", "fee"),
        ("下达时间", "create_time"),
        ("执行时间", "execute_time"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📋 医嘱管理")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 搜索
        sl = QHBoxLayout()
        sl.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按患者姓名/医嘱内容搜索...")
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

        # 操作按钮
        op_layout = QHBoxLayout()
        self.btn_new = QPushButton("📝 新增医嘱")
        self.btn_new.setStyleSheet(
            "background: #27ae60; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_new.clicked.connect(self._open_order_dialog)
        op_layout.addWidget(self.btn_new)

        self.btn_audit = QPushButton("✅ 审核通过")
        self.btn_audit.setStyleSheet(
            "background: #2980b9; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_audit.clicked.connect(lambda: self._change_status("已审核"))
        op_layout.addWidget(self.btn_audit)

        self.btn_exec = QPushButton("💉 执行")
        self.btn_exec.setStyleSheet(
            "background: #e67e22; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_exec.clicked.connect(self._execute_order)
        op_layout.addWidget(self.btn_exec)

        self.btn_stop = QPushButton("⏹️ 停止")
        self.btn_stop.setStyleSheet(
            "background: #c0392b; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_stop.clicked.connect(lambda: self._change_status("已停止"))
        op_layout.addWidget(self.btn_stop)

        op_layout.addStretch()
        layout.addLayout(op_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def _load_data(self):
        try:
            data = MedicalOrderModel.get_all()
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载医嘱数据失败: {e}")

    def _search(self):
        kw = self.search_input.text().strip()
        if not kw:
            self._load_data()
            return
        try:
            data = MedicalOrderModel.search(kw)
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _change_status(self, new_status):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先选择一条医嘱！")
            return
        try:
            MedicalOrderModel.set_status(selected["order_id"], new_status)
            show_info("成功", f"医嘱状态已更新为: {new_status}")
            self._load_data()
        except Exception as e:
            show_error("错误", f"状态更新失败: {e}")

    def _execute_order(self):
        selected = get_selected_row_data(self.table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先选择一条医嘱！")
            return
        if selected.get("status") not in ("已下达", "已审核"):
            show_error("错误", "只能执行已下达或已审核的医嘱！")
            return

        # 选择执行护士
        dialog = NurseSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            nurse_id = dialog.selected_nurse_id
            try:
                MedicalOrderModel.set_status(selected["order_id"], "已执行", nurse_id)
                show_info("成功", "医嘱已执行！（费用已自动生成）")
                self._load_data()
            except Exception as e:
                show_error("错误", f"执行失败: {e}")

    def _open_order_dialog(self):
        dialog = OrderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()


class OrderDialog(QDialog):
    """新增医嘱对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增医嘱")
        self.setMinimumSize(500, 400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        fl = QFormLayout()

        # 住院患者选择
        self.w_record = QComboBox()
        inpatients = InpatientModel.get_current_inpatients()
        self._record_map = {}
        for ip in inpatients:
            label = f"{ip['patient_name']} - {ip['ward_name']} {ip['bed_no']} (住院号:{ip['record_id']})"
            self._record_map[label] = ip["record_id"]
        self.w_record.addItems(self._record_map.keys())
        fl.addRow("患者:", self.w_record)

        # 医生选择
        self.w_doctor = QComboBox()
        doctors = DoctorModel.get_all()
        self._doc_map = {d["name"]: d["doctor_id"] for d in doctors}
        self.w_doctor.addItems(self._doc_map.keys())
        fl.addRow("开嘱医生:", self.w_doctor)

        # 类型
        self.w_type = QComboBox()
        self.w_type.addItems(["药品", "检查", "护理", "手术", "其他"])
        fl.addRow("医嘱类型:", self.w_type)

        # 内容
        self.w_content = QTextEdit()
        self.w_content.setMaximumHeight(80)
        fl.addRow("医嘱内容:", self.w_content)

        # 用量
        self.w_dosage = QLineEdit()
        self.w_dosage.setPlaceholderText("如: 40mg qd 静脉注射")
        fl.addRow("用量/用法:", self.w_dosage)

        # 费用
        self.w_fee = QDoubleSpinBox()
        self.w_fee.setRange(0, 999999.99)
        self.w_fee.setDecimals(2)
        fl.addRow("费用(元):", self.w_fee)

        layout.addLayout(fl)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _submit(self):
        content = self.w_content.toPlainText().strip()
        if not content:
            show_error("错误", "医嘱内容不能为空！")
            return

        data = {
            "record_id": self._record_map.get(self.w_record.currentText()),
            "doctor_id": self._doc_map.get(self.w_doctor.currentText()),
            "nurse_id": None,
            "order_type": self.w_type.currentText(),
            "order_content": content,
            "dosage": self.w_dosage.text().strip(),
            "fee": self.w_fee.value(),
        }

        try:
            MedicalOrderModel.insert(data)
            show_info("成功", "医嘱下达成功！")
            self.accept()
        except Exception as e:
            show_error("错误", f"医嘱下达失败: {e}")


class NurseSelectDialog(QDialog):
    """选择执行护士"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择执行护士")
        self.selected_nurse_id = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请选择执行护士:"))

        self.combo = QComboBox()
        nurses = NurseModel.get_all()
        self._nur_map = {n["name"]: n["nurse_id"] for n in nurses}
        self.combo.addItems(self._nur_map.keys())
        layout.addWidget(self.combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _ok(self):
        name = self.combo.currentText()
        self.selected_nurse_id = self._nur_map.get(name)
        self.accept()
