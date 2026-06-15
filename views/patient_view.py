# views/patient_view.py
# 患者管理界面
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QTextEdit, QPushButton, QLabel, QFormLayout, QHeaderView,
    QMessageBox, QDialog, QDialogButtonBox, QGridLayout, QInputDialog
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont

from models.patient import PatientModel
from models.inpatient import InpatientModel
from models.bed import BedModel
from models.doctor import DoctorModel
from models.nurse import NurseModel
from models.department import DepartmentModel
from utils.helpers import (
    populate_table, get_selected_row_data, set_form_data,
    clear_form, get_form_data, show_info, show_error, confirm
)


class PatientView(QWidget):
    """患者管理页面"""

    COLUMNS = [
        ("编号", "patient_id"),
        ("姓名", "name"),
        ("性别", "gender"),
        ("年龄", "age"),
        ("身份证号", "id_card"),
        ("联系电话", "phone"),
        ("住址", "address"),
        ("血型", "blood_type"),
        ("过敏史", "allergy_history"),
        ("登记日期", "reg_date"),
    ]

    INPATIENT_COLUMNS = [
        ("住院号", "record_id"),
        ("患者名", "patient_name"),
        ("性别", "patient_gender"),
        ("年龄", "patient_age"),
        ("病房", "ward_name"),
        ("床号", "bed_no"),
        ("主治医生", "doctor_name"),
        ("责任护士", "nurse_name"),
        ("入院时间", "admit_date"),
        ("入院诊断", "admit_diagnosis"),
        ("押金", "deposit"),
        ("状态", "status"),
        ("住院天数", "days_in_hospital"),
    ]

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # ===== 顶部标题 =====
        title = QLabel("👨‍⚕️ 患者管理")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 8px 0;")
        layout.addWidget(title)

        # ===== Tab 切换 =====
        tab_layout = QHBoxLayout()
        self.btn_patient = QPushButton("患者信息")
        self.btn_inpatient = QPushButton("住院管理")
        self.btn_patient.setStyleSheet("""
            QPushButton { background: #3498db; color: white; padding: 8px 20px;
                          border-radius: 4px; font-size: 14px; border: none; }
            QPushButton:hover { background: #2980b9; }
        """)
        self.btn_inpatient.setStyleSheet("""
            QPushButton { background: #bdc3c7; color: white; padding: 8px 20px;
                          border-radius: 4px; font-size: 14px; border: none; }
            QPushButton:hover { background: #95a5a6; }
        """)
        self.btn_patient.clicked.connect(lambda: self._switch_tab(0))
        self.btn_inpatient.clicked.connect(lambda: self._switch_tab(1))
        tab_layout.addWidget(self.btn_patient)
        tab_layout.addWidget(self.btn_inpatient)
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # ===== 患者信息 Tab =====
        self.patient_tab = QWidget()
        pt_layout = QVBoxLayout(self.patient_tab)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("按姓名/电话/身份证号搜索...")
        self.patient_search.setMinimumWidth(250)
        self.patient_search.returnPressed.connect(self._search_patients)
        search_layout.addWidget(self.patient_search)
        self.btn_search = QPushButton("🔍 搜索")
        self.btn_search.clicked.connect(self._search_patients)
        search_layout.addWidget(self.btn_search)
        self.btn_refresh_p = QPushButton("🔄 刷新")
        self.btn_refresh_p.clicked.connect(self._load_patients)
        search_layout.addWidget(self.btn_refresh_p)
        search_layout.addStretch()
        pt_layout.addLayout(search_layout)

        # 表单区
        form_group = QGroupBox("患者信息表单")
        form_inner = QVBoxLayout(form_group)
        grid = QGridLayout()

        # 字段定义
        self.patient_widgets = {}

        grid.addWidget(QLabel("姓名*:"), 0, 0)
        self.patient_widgets["name"] = QLineEdit()
        grid.addWidget(self.patient_widgets["name"], 0, 1)

        grid.addWidget(QLabel("性别*:"), 0, 2)
        self.patient_widgets["gender"] = QComboBox()
        self.patient_widgets["gender"].addItems(["男", "女"])
        grid.addWidget(self.patient_widgets["gender"], 0, 3)

        grid.addWidget(QLabel("年龄:"), 1, 0)
        self.patient_widgets["age"] = QSpinBox()
        self.patient_widgets["age"].setRange(0, 150)
        grid.addWidget(self.patient_widgets["age"], 1, 1)

        grid.addWidget(QLabel("身份证号:"), 1, 2)
        self.patient_widgets["id_card"] = QLineEdit()
        grid.addWidget(self.patient_widgets["id_card"], 1, 3)

        grid.addWidget(QLabel("联系电话:"), 2, 0)
        self.patient_widgets["phone"] = QLineEdit()
        grid.addWidget(self.patient_widgets["phone"], 2, 1)

        grid.addWidget(QLabel("血型:"), 2, 2)
        self.patient_widgets["blood_type"] = QComboBox()
        self.patient_widgets["blood_type"].addItems(["", "A", "B", "AB", "O"])
        grid.addWidget(self.patient_widgets["blood_type"], 2, 3)

        grid.addWidget(QLabel("住址:"), 3, 0)
        self.patient_widgets["address"] = QLineEdit()
        grid.addWidget(self.patient_widgets["address"], 3, 1, 1, 3)

        grid.addWidget(QLabel("过敏史:"), 4, 0)
        self.patient_widgets["allergy_history"] = QTextEdit()
        self.patient_widgets["allergy_history"].setMaximumHeight(60)
        grid.addWidget(self.patient_widgets["allergy_history"], 4, 1, 1, 3)

        form_inner.addLayout(grid)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_add_p = QPushButton("➕ 新增")
        self.btn_edit_p = QPushButton("✏️ 修改")
        self.btn_delete_p = QPushButton("🗑️ 删除")
        self.btn_clear_p = QPushButton("🧹 清空")

        for btn in [self.btn_add_p, self.btn_edit_p, self.btn_delete_p, self.btn_clear_p]:
            btn.setStyleSheet("padding: 8px 16px; font-size: 13px;")
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        self.btn_add_p.clicked.connect(self._add_patient)
        self.btn_edit_p.clicked.connect(self._edit_patient)
        self.btn_delete_p.clicked.connect(self._delete_patient)
        self.btn_clear_p.clicked.connect(lambda: clear_form(self.patient_widgets))
        form_inner.addLayout(btn_layout)

        pt_layout.addWidget(form_group)

        # 表格
        self.patient_table = QTableWidget()
        self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patient_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.patient_table.setAlternatingRowColors(True)
        self.patient_table.clicked.connect(self._on_patient_select)
        pt_layout.addWidget(self.patient_table, 1)

        layout.addWidget(self.patient_tab, 1)

        # ===== 住院管理 Tab =====
        self.inpatient_tab = QWidget()
        it_layout = QVBoxLayout(self.inpatient_tab)

        # 搜索
        is_layout = QHBoxLayout()
        is_layout.addWidget(QLabel("搜索:"))
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("按患者姓名/病房搜索...")
        self.inp_search.setMinimumWidth(250)
        self.inp_search.returnPressed.connect(self._search_inpatients)
        is_layout.addWidget(self.inp_search)
        self.btn_inp_search = QPushButton("🔍 搜索")
        self.btn_inp_search.clicked.connect(self._search_inpatients)
        is_layout.addWidget(self.btn_inp_search)
        self.btn_inp_refresh = QPushButton("🔄 刷新")
        self.btn_inp_refresh.clicked.connect(self._load_inpatients)
        is_layout.addWidget(self.btn_inp_refresh)
        is_layout.addStretch()
        it_layout.addLayout(is_layout)

        # 床位快速操作
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("[快捷操作]"))
        self.btn_admit = QPushButton("🏥 办理入院")
        self.btn_admit.setStyleSheet(
            "background: #27ae60; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_admit.clicked.connect(self._open_admit_dialog)
        op_layout.addWidget(self.btn_admit)

        self.btn_discharge = QPushButton("🏁 办理出院")
        self.btn_discharge.setStyleSheet(
            "background: #e67e22; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_discharge.clicked.connect(self._discharge_patient)
        op_layout.addWidget(self.btn_discharge)

        self.btn_transfer = QPushButton("🔄 转床")
        self.btn_transfer.setStyleSheet(
            "background: #9b59b6; color: white; padding: 8px 16px; "
            "border-radius: 4px; font-size: 13px;")
        self.btn_transfer.clicked.connect(self._transfer_bed)
        op_layout.addWidget(self.btn_transfer)

        op_layout.addStretch()
        it_layout.addLayout(op_layout)

        # 表格
        self.inp_table = QTableWidget()
        self.inp_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inp_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inp_table.setAlternatingRowColors(True)
        it_layout.addWidget(self.inp_table, 1)

        layout.addWidget(self.inpatient_tab, 1)

        # 默认显示患者信息 Tab
        self.inpatient_tab.hide()
        self._current_tab = 0

    # ==================== Tab 切换 ====================

    def _switch_tab(self, tab):
        self._current_tab = tab
        if tab == 0:
            self.patient_tab.show()
            self.inpatient_tab.hide()
            self.btn_patient.setStyleSheet(
                "background: #3498db; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self.btn_inpatient.setStyleSheet(
                "background: #bdc3c7; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self._load_patients()
        else:
            self.patient_tab.hide()
            self.inpatient_tab.show()
            self.btn_inpatient.setStyleSheet(
                "background: #3498db; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self.btn_patient.setStyleSheet(
                "background: #bdc3c7; color: white; padding: 8px 20px; "
                "border-radius: 4px; font-size: 14px; border: none;")
            self._load_inpatients()

    # ==================== 患者 CRUD ====================

    def _load_patients(self):
        try:
            data = PatientModel.get_all()
            populate_table(self.patient_table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"加载患者数据失败: {e}")

    def _search_patients(self):
        kw = self.patient_search.text().strip()
        if not kw:
            self._load_patients()
            return
        try:
            data = PatientModel.search(kw)
            populate_table(self.patient_table, data, self.COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _on_patient_select(self):
        data = get_selected_row_data(self.patient_table, self.COLUMNS)
        if data:
            set_form_data(self.patient_widgets, data)

    def _add_patient(self):
        data = get_form_data(self.patient_widgets)
        if not data["name"] or not data["gender"]:
            show_error("错误", "姓名和性别为必填项！")
            return
        try:
            PatientModel.insert(data)
            show_info("成功", f"患者 {data['name']} 添加成功！")
            clear_form(self.patient_widgets)
            self._load_patients()
        except Exception as e:
            show_error("错误", f"添加失败: {e}")

    def _edit_patient(self):
        selected = get_selected_row_data(self.patient_table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        data = get_form_data(self.patient_widgets)
        data["patient_id"] = selected["patient_id"]
        if not data["name"]:
            show_error("错误", "姓名为必填项！")
            return
        try:
            PatientModel.update(data)
            show_info("成功", f"患者 {data['name']} 修改成功！")
            self._load_patients()
        except Exception as e:
            show_error("错误", f"修改失败: {e}")

    def _delete_patient(self):
        selected = get_selected_row_data(self.patient_table, self.COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择一条记录！")
            return
        if not confirm("确认删除", f"确定要删除患者 [{selected['name']}] 吗？"):
            return
        try:
            PatientModel.delete(selected["patient_id"])
            show_info("成功", "删除成功！")
            clear_form(self.patient_widgets)
            self._load_patients()
        except Exception as e:
            show_error("错误", f"删除失败（可能有关联的住院记录）: {e}")

    # ==================== 住院管理 ====================

    def _load_inpatients(self):
        try:
            data = InpatientModel.get_current_inpatients()
            populate_table(self.inp_table, data, self.INPATIENT_COLUMNS)
        except Exception as e:
            show_error("错误", f"加载住院数据失败: {e}")

    def _search_inpatients(self):
        kw = self.inp_search.text().strip()
        if not kw:
            self._load_inpatients()
            return
        try:
            data = InpatientModel.search(kw)
            populate_table(self.inp_table, data, self.INPATIENT_COLUMNS)
        except Exception as e:
            show_error("错误", f"搜索失败: {e}")

    def _open_admit_dialog(self):
        dialog = AdmitDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self._load_inpatients()

    def _discharge_patient(self):
        selected = get_selected_row_data(self.inp_table, self.INPATIENT_COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择要出院的记录！")
            return
        if selected.get("status") != "在院":
            show_error("错误", "只能为在院患者办理出院！")
            return
        if not confirm("确认出院", f"确定为患者 [{selected['patient_name']}] 办理出院吗？\n请确保费用已结清！"):
            return

        discharge_diag, ok = QInputDialog.getText(
            self, "出院诊断", "请输入出院诊断:")
        if not ok:
            return
        try:
            InpatientModel.discharge(selected["record_id"], discharge_diag)
            show_info("成功", f"患者 {selected['patient_name']} 已办理出院！")
            self._load_inpatients()
        except Exception as e:
            show_error("错误", f"出院失败: {e}")

    def _transfer_bed(self):
        selected = get_selected_row_data(self.inp_table, self.INPATIENT_COLUMNS)
        if not selected:
            show_error("错误", "请先在表格中选择要转床的患者！")
            return
        if selected.get("status") != "在院":
            show_error("错误", "只能为在院患者转床！")
            return

        # 显示可用病床选择对话框
        dialog = BedSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_bed_id = dialog.selected_bed_id
            try:
                InpatientModel.transfer_bed(selected["record_id"], new_bed_id)
                show_info("成功", f"转床成功！")
                self._load_inpatients()
            except Exception as e:
                show_error("错误", f"转床失败: {e}")

    def _load_data(self):
        self._load_patients()


class AdmitDialog(QDialog):
    """入院办理对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("办理入院登记")
        self.setMinimumSize(600, 500)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.w_name = QLineEdit()
        form.addRow("患者姓名*:", self.w_name)

        self.w_gender = QComboBox()
        self.w_gender.addItems(["男", "女"])
        form.addRow("性别*:", self.w_gender)

        self.w_age = QSpinBox()
        self.w_age.setRange(0, 150)
        self.w_age.setValue(30)
        form.addRow("年龄:", self.w_age)

        self.w_id_card = QLineEdit()
        form.addRow("身份证号:", self.w_id_card)

        self.w_phone = QLineEdit()
        form.addRow("联系电话:", self.w_phone)

        self.w_address = QLineEdit()
        form.addRow("住址:", self.w_address)

        self.w_blood = QComboBox()
        self.w_blood.addItems(["", "A", "B", "AB", "O"])
        form.addRow("血型:", self.w_blood)

        self.w_allergy = QTextEdit()
        self.w_allergy.setMaximumHeight(50)
        form.addRow("过敏史:", self.w_allergy)

        # 科室选择
        self.w_dept = QComboBox()
        depts = DepartmentModel.get_all()
        self._dept_data = {d["dept_name"]: d["dept_id"] for d in depts}
        self.w_dept.addItems(self._dept_data.keys())
        self.w_dept.currentIndexChanged.connect(self._on_dept_changed)
        form.addRow("科室:", self.w_dept)

        # 病床选择
        self.w_bed = QComboBox()
        form.addRow("分配病床:", self.w_bed)

        # 医生选择
        self.w_doctor = QComboBox()
        form.addRow("主治医生:", self.w_doctor)

        # 护士选择
        self.w_nurse = QComboBox()
        form.addRow("责任护士:", self.w_nurse)

        self.w_diagnosis = QLineEdit()
        form.addRow("入院诊断:", self.w_diagnosis)

        self.w_deposit = QDoubleSpinBox()
        self.w_deposit.setRange(0, 9999999.99)
        self.w_deposit.setDecimals(2)
        self.w_deposit.setValue(2000.00)
        form.addRow("住院押金:", self.w_deposit)

        layout.addLayout(form)

        # 初始化科室数据
        self._on_dept_changed(0)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_dept_changed(self, idx):
        dept_name = self.w_dept.currentText()
        dept_id = self._dept_data.get(dept_name)

        # 更新病床
        self.w_bed.clear()
        if dept_id:
            beds = BedModel.get_available_by_dept(dept_id)
            self._bed_data = {f"{b['ward_name']} {b['bed_no']} (¥{b['price_per_day']}/天)": b["bed_id"] for b in beds}
            self.w_bed.addItems(self._bed_data.keys())
        else:
            self._bed_data = {}

        # 更新医生
        self.w_doctor.clear()
        if dept_id:
            doctors = DoctorModel.get_by_dept(dept_id)
            self._doc_data = {d["name"]: d["doctor_id"] for d in doctors}
            self.w_doctor.addItems(self._doc_data.keys())
        else:
            self._doc_data = {}

        # 更新护士
        self.w_nurse.clear()
        if dept_id:
            nurses = NurseModel.get_by_dept(dept_id)
            self._nur_data = {n["name"]: n["nurse_id"] for n in nurses}
            self.w_nurse.addItems(self._nur_data.keys())
        else:
            self._nur_data = {}

    def _submit(self):
        name = self.w_name.text().strip()
        if not name:
            show_error("错误", "患者姓名不能为空！")
            return
        if self.w_bed.count() == 0:
            show_error("错误", "所选科室没有可用病床！")
            return

        data = {
            "name": name,
            "gender": self.w_gender.currentText(),
            "age": self.w_age.value(),
            "id_card": self.w_id_card.text().strip(),
            "phone": self.w_phone.text().strip(),
            "address": self.w_address.text().strip(),
            "blood_type": self.w_blood.currentText(),
            "allergy_history": self.w_allergy.toPlainText().strip(),
            "bed_id": self._bed_data.get(self.w_bed.currentText()),
            "doctor_id": self._doc_data.get(self.w_doctor.currentText()),
            "nurse_id": self._nur_data.get(self.w_nurse.currentText()),
            "admit_diagnosis": self.w_diagnosis.text().strip(),
            "deposit": self.w_deposit.value(),
        }

        if not data["bed_id"]:
            show_error("错误", "请选择病床！")
            return

        try:
            # 使用存储过程一键入院
            result = InpatientModel.admit_with_procedure(data)
            if result:
                show_info("成功", f"患者 {name} 入院成功！")
            self.accept()
        except Exception as e:
            show_error("错误", f"入院失败: {e}")


class BedSelectDialog(QDialog):
    """转床 - 病床选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择目标病床")
        self.setMinimumSize(400, 200)
        self.selected_bed_id = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请选择要转入的病床:"))

        self.bed_combo = QComboBox()
        beds = BedModel.get_available()
        self._bed_data = {}
        for b in beds:
            label = f"{b['dept_name']} - {b['ward_name']} {b['bed_no']} ({b['bed_type']})"
            self._bed_data[label] = b["bed_id"]
            self.bed_combo.addItem(label)
        layout.addWidget(self.bed_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _ok(self):
        label = self.bed_combo.currentText()
        if label in self._bed_data:
            self.selected_bed_id = self._bed_data[label]
            self.accept()
        else:
            show_error("错误", "请选择病床！")
