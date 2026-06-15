# views/statistics_view.py
# 统计报表界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QPushButton, QLabel, QComboBox, QDateEdit, QHeaderView,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from db.connection import db
from utils.helpers import populate_table, show_error


class StatisticsView(QWidget):
    """统计报表页面"""

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_dept_rate()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📊 统计报表")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # 统计按钮
        btn_layout = QHBoxLayout()

        self.btn_dept_rate = QPushButton("📈 科室占用率")
        self.btn_dept_rate.clicked.connect(self._load_dept_rate)
        btn_layout.addWidget(self.btn_dept_rate)

        self.btn_ward_rate = QPushButton("🏥 病房使用率")
        self.btn_ward_rate.clicked.connect(self._load_ward_rate)
        btn_layout.addWidget(self.btn_ward_rate)

        self.btn_doctor_workload = QPushButton("👨‍⚕️ 医生工作量")
        self.btn_doctor_workload.clicked.connect(self._load_doctor_workload)
        btn_layout.addWidget(self.btn_doctor_workload)

        self.btn_order_view = QPushButton("📋 医嘱执行情况")
        self.btn_order_view.clicked.connect(self._load_order_view)
        btn_layout.addWidget(self.btn_order_view)

        btn_layout.addStretch()

        for btn in [self.btn_dept_rate, self.btn_ward_rate, self.btn_doctor_workload, self.btn_order_view]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #3498db; color: white; padding: 10px 20px;
                    border-radius: 6px; font-size: 14px; border: none;
                }
                QPushButton:hover { background: #2980b9; }
            """)

        layout.addLayout(btn_layout)

        # 日期筛选（医生工作量用）
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("结束日期:"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        filter_layout.addWidget(self.end_date)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # 当前统计标题
        self.stat_title = QLabel("科室病床占用率统计")
        self.stat_title.setFont(QFont("Microsoft YaHei", 13))
        self.stat_title.setStyleSheet("color: #2c3e50; padding: 4px 0;")
        layout.addWidget(self.stat_title)

        # 表格
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def _load_dept_rate(self):
        self.stat_title.setText("科室病床占用率统计")
        try:
            results = db.call_procedure("sp_dept_occupancy_rate")
            if results:
                cols = [
                    ("科室编号", "dept_id"),
                    ("科室名称", "科室名称"),
                    ("总床位数", "总床位数"),
                    ("已占用", "已占用"),
                    ("空闲", "空闲"),
                    ("维修中", "维修中"),
                    ("占用率(%)", "占用率百分比"),
                ]
                populate_table(self.table, results[0], cols)
        except Exception as e:
            show_error("错误", f"统计失败: {e}")

    def _load_ward_rate(self):
        self.stat_title.setText("病房使用率统计")
        try:
            results = db.call_procedure("sp_ward_usage_rate")
            if results:
                cols = [
                    ("编号", "ward_id"),
                    ("病房名称", "病房名称"),
                    ("科室", "所属科室"),
                    ("类型", "病房类型"),
                    ("容量", "总床位数"),
                    ("已占用", "已占用数"),
                    ("空闲", "空闲数"),
                    ("使用率(%)", "使用率百分比"),
                    ("日费(元)", "日床位费"),
                ]
                populate_table(self.table, results[0], cols)
        except Exception as e:
            show_error("错误", f"统计失败: {e}")

    def _load_doctor_workload(self):
        self.stat_title.setText("医生工作量统计")
        start = self.start_date.dateTime().toString("yyyy-MM-dd")
        end = self.end_date.dateTime().toString("yyyy-MM-dd")
        try:
            results = db.call_procedure("sp_doctor_workload", (start, end))
            if results:
                cols = [
                    ("编号", "doctor_id"),
                    ("姓名", "医生姓名"),
                    ("职称", "职称"),
                    ("科室", "科室"),
                    ("负责患者数", "负责患者数"),
                    ("下达医嘱数", "下达医嘱数"),
                    ("已执行医嘱数", "已执行医嘱数"),
                ]
                populate_table(self.table, results[0], cols)
        except Exception as e:
            show_error("错误", f"统计失败: {e}")

    def _load_order_view(self):
        self.stat_title.setText("医嘱执行情况一览")
        try:
            data = db.execute_query("SELECT * FROM v_order_execution")
            cols = [
                ("编号", "order_id"),
                ("患者", "patient_name"),
                ("病房", "ward_name"),
                ("床号", "bed_no"),
                ("类型", "order_type"),
                ("内容", "order_content"),
                ("用法", "dosage"),
                ("医生", "doctor_name"),
                ("护士", "nurse_name"),
                ("状态", "status"),
                ("费用", "fee"),
                ("下达时间", "create_time"),
                ("执行时间", "execute_time"),
                ("耗时(分)", "execute_minutes"),
            ]
            populate_table(self.table, data, cols)
        except Exception as e:
            show_error("错误", f"查询失败: {e}")
