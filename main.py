# main.py
# 医院病房管理系统 - 主程序入口
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from views.login_dialog import LoginDialog
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # 全局样式
    app.setStyle("Fusion")
    app.setStyleSheet("""
        * {
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
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
        QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
            padding: 6px 10px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            font-size: 13px;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #3498db;
        }
        QPushButton {
            padding: 8px 16px;
            font-size: 13px;
            border-radius: 4px;
            border: none;
        }
        QPushButton#btn_primary {
            background-color: #3498db;
            color: white;
        }
        QPushButton#btn_danger {
            background-color: #e74c3c;
            color: white;
        }
        QPushButton#btn_success {
            background-color: #27ae60;
            color: white;
        }
        QLabel {
            font-size: 13px;
        }
    """)

    # ========== 登录 ==========
    login = LoginDialog()
    if login.exec_() != LoginDialog.Accepted:
        sys.exit(0)

    # 登录成功
    user_info = login.logged_in_user
    window = MainWindow()
    window.set_user_info(user_info)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
