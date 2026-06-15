# models/patient.py
from db.connection import db


class PatientModel:
    """患者表 CRUD"""

    TABLE = "patients"

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM patients ORDER BY patient_id DESC"
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, patient_id):
        sql = "SELECT * FROM patients WHERE patient_id = %s"
        return db.execute_query(sql, (patient_id,), fetch_one=True)

    @classmethod
    def search(cls, keyword):
        sql = ("SELECT * FROM patients WHERE name LIKE %s OR phone LIKE %s "
               "OR id_card LIKE %s ORDER BY patient_id DESC")
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO patients (name, gender, age, id_card, phone, "
               "address, blood_type, allergy_history) "
               "VALUES (%(name)s, %(gender)s, %(age)s, %(id_card)s, "
               "%(phone)s, %(address)s, %(blood_type)s, %(allergy_history)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE patients SET name=%(name)s, gender=%(gender)s, "
               "age=%(age)s, id_card=%(id_card)s, phone=%(phone)s, "
               "address=%(address)s, blood_type=%(blood_type)s, "
               "allergy_history=%(allergy_history)s "
               "WHERE patient_id=%(patient_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def delete(cls, patient_id):
        sql = "DELETE FROM patients WHERE patient_id = %s"
        return db.execute_update(sql, (patient_id,))

    @classmethod
    def get_fee_summary(cls, patient_id):
        """调用存储过程查询患者费用"""
        return db.call_procedure("sp_patient_total_fee", (patient_id,))
