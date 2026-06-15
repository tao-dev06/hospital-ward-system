# views/login_dialog.py
# 登录对话框
import hashlib
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
from db.connection import db


class LoginDialog(QDialog):
    """登录窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("医院病房管理系统 - 登录")
        self.setFixedSize(420, 380)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.logged_in_user = None

        self._init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                font-size: 14px;
                background: white;
            }
            QPushButton#login_btn {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton#login_btn:hover {
                background-color: #2980b9;
            }
            QPushButton#login_btn:pressed {
                background-color: #2471a3;
            }
        """)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)

        # 标题
        title = QLabel("医院病房管理系统")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 图标占位
        icon_label = QLabel("🏥")
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        layout.addSpacing(5)

        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        layout.addWidget(QLabel("用户名:"))
        layout.addWidget(self.username_input)

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("密码:"))
        layout.addWidget(self.password_input)

        # 登录按钮
        self.login_btn = QPushButton("登  录")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.clicked.connect(self._do_login)
        layout.addWidget(self.login_btn)

        # 提示
        hint = QLabel("默认账号: admin | doctor1 | nurse1 | cashier1\n默认密码: admin123 / 123456")
        hint.setFont(QFont("Microsoft YaHei", 9))
        hint.setStyleSheet("color: #95a5a6;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        # 回车键触发登录
        self.username_input.returnPressed.connect(self._do_login)
        self.password_input.returnPressed.connect(self._do_login)

        # 默认焦点
        self.username_input.setFocus()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码！")
            return

        try:
            pwd_hash = hashlib.md5(password.encode()).hexdigest()
            sql = "SELECT user_id, username, role, real_name FROM users WHERE username = %s AND password = %s"
            user = db.execute_query(sql, (username, pwd_hash), fetch_one=True)

            if user:
                self.logged_in_user = {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "role": user["role"],
                    "real_name": user["real_name"],
                }
                self.accept()
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误！")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库连接失败: {e}")
