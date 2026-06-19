# views/login_dialog.py
import hashlib
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db.connection import db


class LoginDialog(QDialog):
    """登录窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("医院病房管理系统 - 登录")
        self.resize(680, 620)
        self.setMinimumSize(340, 340)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.logged_in_user = None

        self._init_ui()
        self._apply_responsive_sizes()

    def _scale_value(self, base_value, scale):
        return max(1, int(round(base_value * scale)))

    def _current_scale(self):
        width_scale = self.width() / 420
        height_scale = self.height() / 400
        return max(0.82, min(width_scale, height_scale, 1.75))

    def _apply_responsive_sizes(self):
        scale = self._current_scale()

        self.layout.setSpacing(self._scale_value(15, scale))
        self.layout.setContentsMargins(
            self._scale_value(50, scale),
            self._scale_value(30, scale),
            self._scale_value(50, scale),
            self._scale_value(30, scale),
        )
        self.icon_label.setFont(QFont("Segoe UI Emoji", self._scale_value(48, scale)))
        self.hint.setFont(QFont("Microsoft YaHei", self._scale_value(9, scale)))
        self.username_label.setFont(QFont("Microsoft YaHei", self._scale_value(13, scale)))
        self.password_label.setFont(QFont("Microsoft YaHei", self._scale_value(13, scale)))
        self.username_input.setFixedHeight(self._scale_value(42, scale))
        self.password_input.setFixedHeight(self._scale_value(42, scale))
        self.login_btn.setFixedHeight(self._scale_value(44, scale))

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel#title {
                font-size: %dpx;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#field_label {
                font-size: %dpx;
                color: #2c3e50;
            }
            QLabel#hint {
                font-size: %dpx;
                color: #95a5a6;
            }
            QLineEdit {
                padding: %dpx %dpx;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                font-size: %dpx;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton#login_btn {
                background-color: #3498db;
                color: white;
                padding: %dpx %dpx;
                font-size: %dpx;
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
        """ % (
            self._scale_value(22, scale),
            self._scale_value(13, scale),
            self._scale_value(9, scale),
            self._scale_value(6, scale),
            self._scale_value(12, scale),
            self._scale_value(14, scale),
            self._scale_value(8, scale),
            self._scale_value(12, scale),
            self._scale_value(16, scale),
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_responsive_sizes()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(50, 30, 50, 30)

        title = QLabel("医院病房管理系统")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        self.title = title
        self.layout.addWidget(title)

        icon_label = QLabel("🏥")
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label = icon_label
        self.layout.addWidget(icon_label)

        self.layout.addSpacing(5)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFixedHeight(42)
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.username_label = QLabel("用户名:")
        self.username_label.setObjectName("field_label")
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password_label = QLabel("密码:")
        self.password_label.setObjectName("field_label")
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.login_btn = QPushButton("登 录")
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setFixedHeight(44)
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_btn.clicked.connect(self._do_login)
        self.layout.addWidget(self.login_btn)

        hint = QLabel("默认账号: admin | doctor1 | nurse1 | cashier1\n默认密码: admin123 / 123456")
        hint.setObjectName("hint")
        hint.setFont(QFont("Microsoft YaHei", 9))
        hint.setAlignment(Qt.AlignCenter)
        self.hint = hint
        self.layout.addWidget(hint)

        self.username_input.returnPressed.connect(self._do_login)
        self.password_input.returnPressed.connect(self._do_login)

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
