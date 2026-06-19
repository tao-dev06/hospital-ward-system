# views/main_window.py
# 主窗口框架
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QColor
from utils.responsive import ResponsiveScaler


class MainWindow(QMainWindow):
    """医院病房管理系统 - 主窗口"""

    DB_CONNECTED = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("医院病房管理系统")
        self.resize(1200, 750)
        self.setMinimumSize(900, 560)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QListWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 15px;
                border: none;
                min-width: 160px;
                max-width: 160px;
            }
            QListWidget::item {
                padding: 14px 16px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
            QWidget {
                font-size: 13px;
            }
            QLabel {
                font-size: 13px;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                padding: 6px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
                min-height: 24px;
            }
            QTextEdit {
                padding: 6px 10px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
            QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 13px;
                border-radius: 4px;
                min-height: 24px;
            }
            QTableWidget {
                font-size: 13px;
                gridline-color: #ddd;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
        """)

        # 先检查数据库连接
        try:
            from db.connection import db
            conn = db.connect()
            conn.ping()
            self.DB_CONNECTED = True
        except Exception:
            self.DB_CONNECTED = False

        self._init_ui()
        self.responsive_scaler = ResponsiveScaler(self, base_size=(1200, 750), min_scale=0.75, max_scale=1.6)
        self.responsive_scaler.apply()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "responsive_scaler"):
            self.responsive_scaler.apply()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== 左侧导航栏 ==========
        self.nav_list = QListWidget()

        self._nav_items = [
            ("🏠 病房管理", 0),
            ("🛏️ 病床监控", 1),
            ("👨‍⚕️ 患者管理", 2),
            ("👨‍🔬 医生管理", 3),
            ("👩‍⚕️ 护士管理", 4),
            ("📋 医嘱管理", 5),
            ("💰 费用管理", 6),
            ("📊 统计报表", 7),
        ]
        for label, idx in self._nav_items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, idx)
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)

        layout.addWidget(self.nav_list)

        # ========== 右侧内容区域 ==========
        self.stack = QStackedWidget()
        self._pages = {}

        if self.DB_CONNECTED:
            # 数据库可用：加载真实页面
            from views.patient_view import PatientView
            from views.ward_view import WardView
            from views.bed_view import BedView
            from views.doctor_view import DoctorView
            from views.nurse_view import NurseView
            from views.order_view import OrderView
            from views.charge_view import ChargeView
            from views.statistics_view import StatisticsView

            self._pages[0] = WardView()
            self._pages[1] = BedView()
            self._pages[2] = PatientView()
            self._pages[3] = DoctorView()
            self._pages[4] = NurseView()
            self._pages[5] = OrderView()
            self._pages[6] = ChargeView()
            self._pages[7] = StatisticsView()
        else:
            # 数据库不可用：显示离线提示页面
            page_names = [
                "🏠 病房管理", "🛏️ 病床监控", "👨‍⚕️ 患者管理",
                "👨‍🔬 医生管理", "👩‍⚕️ 护士管理", "📋 医嘱管理",
                "💰 费用管理", "📊 统计报表"
            ]
            for idx, name in enumerate(page_names):
                page = self._create_offline_page(name, idx)
                self._pages[idx] = page

        for idx, page in self._pages.items():
            self.stack.addWidget(page)

        self.stack.setCurrentIndex(0)
        layout.addWidget(self.stack, 1)

        # ========== 状态栏 ==========
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        if self.DB_CONNECTED:
            self.status_label = QLabel("  ✅ 数据库连接正常 | 欢迎使用医院病房管理系统")
            self.status_label.setStyleSheet("color: #27ae60;")
        else:
            self.status_label = QLabel("  ⚠️ 数据库未连接 | UI 预览模式（请先配置 db/config.py 并启动 MySQL）")
            self.status_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        self.status_bar.addWidget(self.status_label)

        # 显示登录用户信息
        self._update_user_info()

    def set_user_info(self, user_info):
        """设置当前登录用户"""
        self._user_info = user_info
        self._update_user_info()

    def _update_user_info(self):
        """更新状态栏的用户信息"""
        if hasattr(self, '_user_info') and self._user_info:
            role = self._user_info.get("role", "")
            name = self._user_info.get("real_name", "")
            self.status_label.setText(
                f"  👤 {name}（{role}）| ✅ 数据库连接正常 | 欢迎使用医院病房管理系统"
            )

    def _create_offline_page(self, name, idx):
        """创建离线预览页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel(name[0:2])
        icon.setFont(QFont("Microsoft YaHei", 64))
        icon.setAlignment(Qt.AlignCenter)

        title_label = QLabel(name)
        title_label.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")

        hint = QLabel("数据库未连接，此处将显示数据表格和操作面板")
        hint.setFont(QFont("Microsoft YaHei", 13))
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #95a5a6; padding: 20px;")

        steps = QLabel(
            "📋 启动步骤：\n"
            "1. 启动 MySQL 服务\n"
            "2. 执行 sql/ 目录下的 SQL 脚本\n"
            "3. 修改 db/config.py 中的数据库密码\n"
            "4. 重新启动本程序"
        )
        steps.setFont(QFont("Microsoft YaHei", 12))
        steps.setAlignment(Qt.AlignCenter)
        steps.setStyleSheet(
            "color: #2c3e50; background: #fff; padding: 24px; "
            "border: 1px solid #bdc3c7; border-radius: 8px;"
        )

        layout.addStretch(2)
        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(hint)
        layout.addSpacing(20)
        layout.addWidget(steps, alignment=Qt.AlignCenter)
        layout.addStretch(3)

        return page

    def _on_nav_changed(self, index):
        item = self.nav_list.currentItem()
        if item:
            page_idx = item.data(Qt.UserRole)
            self.stack.setCurrentIndex(page_idx)
