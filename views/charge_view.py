# views/charge_view.py
# 费用管理界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit, QPushButton, QLabel,
    QDialog, QDialogButtonBox, QFormLayout, QDateEdit,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from models.charge import ChargeModel
from models.inpatient import InpatientModel
from models.patient import PatientModel
from utils.helpers import (
    populate_table, get_selected_row_data, show_info, show_error, confirm
)


class ChargeView(QWidget):
    """费用管理页面"""

    COLUMNS = [
        ("编号", "charge_id"),
        ("患者", "patient_name"),
        ("病房", "ward_name"),
        ("床号", "bed_no"),
        ("费用类型", "charge_type"),
        ("金额(元)", "amount"),
        ("收费日期", "charge_date"),
        ("备注", "remark"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("💰 费用管理")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 搜索
        sl = QHBoxLayout()
        sl.addWidget(QLabel("搜索患者:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按姓名搜索...")
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
        self.btn_add_charge = QPushButton("💳 手动收费")
        self.btn_add_charge.setStyleSheet(
            "background: #27ae60; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_add_charge.clicked.connect(self._open_charge_dialog)
        op_layout.addWidget(self.btn_add_charge)

        self.btn_bed_fee = QPushButton("🏨 生成当日床位费")
        self.btn_bed_fee.setStyleSheet(
            "background: #2980b9; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_bed_fee.clicked.connect(self._gen_bed_fee)
        op_layout.addWidget(self.btn_bed_fee)

        self.btn_fee_summary = QPushButton("📄 费用结算查看")
        self.btn_fee_summary.setStyleSheet(
            "background: #8e44ad; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_fee_summary.clicked.connect(self._view_summary)
        op_layout.addWidget(self.btn_fee_summary)

        self.btn_statistics = QPushButton("📊 收入统计")
        self.btn_statistics.setStyleSheet(
            "background: #e67e22; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_statistics.clicked.connect(self._revenue_stats)
        op_layout.addWidget(self.btn_statistics)

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
            data = ChargeModel.get_all()
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载费用数据失败: {e}")

    def _search(self):
        kw = self.search_input.text().strip()
        if not kw:
            self._load_data()
            return
        try:
            data = ChargeModel.search(kw)
            populate_table(self.table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _open_charge_dialog(self):
        dialog = ChargeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_data()

    def _gen_bed_fee(self):
        """为所有在院患者生成当日床位费"""
        if not confirm("确认生成", "将为所有在院患者生成当日床位费，确认吗？"):
            return
        try:
            inpatients = InpatientModel.get_current_inpatients()
            count = 0
            for ip in inpatients:
                try:
                    ChargeModel.add_daily_bed_charge(ip["record_id"])
                    count += 1
                except Exception:
                    pass  # 当天已生成则跳过
            show_info("成功", f"已为 {count} 名在院患者生成当日床位费！")
            self._load_data()
        except Exception as e:
            show_error("错误", f"生成失败: {e}")

    def _view_summary(self):
        dialog = SummaryDialog(self)
        dialog.exec_()

    def _revenue_stats(self):
        dialog = RevenueDialog(self)
        dialog.exec_()


class ChargeDialog(QDialog):
    """手动收费"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("手动录入费用")
        self.setMinimumSize(400, 250)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        fl = QFormLayout()

        self.w_record = QComboBox()
        inpatients = InpatientModel.get_current_inpatients()
        self._rec_map = {}
        for ip in inpatients:
            label = f"{ip['patient_name']} - {ip['ward_name']} {ip['bed_no']}"
            self._rec_map[label] = ip["record_id"]
        self.w_record.addItems(self._rec_map.keys())
        fl.addRow("患者:", self.w_record)

        self.w_type = QComboBox()
        self.w_type.addItems(["药费", "检查费", "护理费", "手术费", "其他"])
        fl.addRow("费用类型:", self.w_type)

        self.w_amount = QDoubleSpinBox()
        self.w_amount.setRange(0, 999999.99)
        self.w_amount.setDecimals(2)
        self.w_amount.setValue(100.00)
        fl.addRow("金额:", self.w_amount)

        self.w_remark = QLineEdit()
        fl.addRow("备注:", self.w_remark)

        layout.addLayout(fl)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _submit(self):
        data = {
            "record_id": self._rec_map.get(self.w_record.currentText()),
            "charge_type": self.w_type.currentText(),
            "amount": self.w_amount.value(),
            "remark": self.w_remark.text().strip(),
        }
        try:
            ChargeModel.insert(data)
            show_info("成功", "费用录入成功！")
            self.accept()
        except Exception as e:
            show_error("错误", f"录入失败: {e}")


class SummaryDialog(QDialog):
    """费用结算查看"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("患者费用结算")
        self.setMinimumSize(600, 400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 选择患者
        row = QHBoxLayout()
        row.addWidget(QLabel("选择患者:"))
        self.patient_combo = QComboBox()
        patients = PatientModel.get_all()
        self._pat_map = {p["name"]: p["patient_id"] for p in patients}
        self.patient_combo.addItems(self._pat_map.keys())
        row.addWidget(self.patient_combo)
        self.btn_query = QPushButton("查询费用")
        self.btn_query.clicked.connect(self._query)
        row.addWidget(self.btn_query)
        row.addStretch()
        layout.addLayout(row)

        # 结果表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 1)

        # 合计
        self.summary_label = QLabel("请选择患者后点击查询")
        self.summary_label.setFont(QFont("Microsoft YaHei", 12))
        self.summary_label.setStyleSheet("padding: 8px; background: #f0f0f0;")
        layout.addWidget(self.summary_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _query(self):
        patient_id = self._pat_map.get(self.patient_combo.currentText())
        if not patient_id:
            return
        try:
            results = PatientModel.get_fee_summary(patient_id)
            if results and len(results) >= 2:
                # results[0] = 费用明细, results[1] = 合计
                detail = results[0]
                summary = results[1]

                cols = [
                    ("编号", "charge_id"),
                    ("费用类型", "费用类型"),
                    ("金额", "金额"),
                    ("日期", "收费日期"),
                    ("备注", "备注"),
                    ("病房", "病房"),
                ]
                populate_table(self.table, detail, cols)

                if summary:
                    s = summary[0]
                    self.summary_label.setText(
                        f"患者: {s.get('患者姓名', '')} | "
                        f"总费用: ¥{s.get('总费用', 0):.2f} | "
                        f"已缴押金: ¥{s.get('押金', 0):.2f} | "
                        f"待缴金额: ¥{s.get('待缴金额', 0):.2f}"
                    )
        except Exception as e:
            show_error("错误", f"查询失败: {e}")


class RevenueDialog(QDialog):
    """收入统计"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("收入统计报表")
        self.setMinimumSize(600, 450)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 日期选择
        row = QHBoxLayout()
        row.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        row.addWidget(self.start_date)
        row.addWidget(QLabel("结束日期:"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        row.addWidget(self.end_date)
        self.btn_query = QPushButton("查询统计")
        self.btn_query.clicked.connect(self._query)
        row.addWidget(self.btn_query)
        row.addStretch()
        layout.addLayout(row)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _query(self):
        start = self.start_date.dateTime().toString("yyyy-MM-dd")
        end = self.end_date.dateTime().toString("yyyy-MM-dd")
        try:
            results = ChargeModel.get_revenue_statistics(start, end)
            if results and len(results) >= 2:
                type_stats = results[0]  # 按费用类型
                cols = [
                    ("费用类型", "费用类型"),
                    ("笔数", "收费笔数"),
                    ("总金额", "总金额"),
                    ("平均金额", "平均金额"),
                ]
                populate_table(self.table, type_stats, cols)
        except Exception as e:
            show_error("错误", f"统计失败: {e}")
