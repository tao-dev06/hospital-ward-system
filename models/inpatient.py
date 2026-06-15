# models/inpatient.py
from db.connection import db


class InpatientModel:
    """住院记录表 CRUD"""

    TABLE = "inpatient_records"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT ir.*, p.name AS patient_name, p.gender AS patient_gender,
                   p.age AS patient_age, b.bed_no, w.ward_name,
                   d.name AS doctor_name, n.name AS nurse_name
            FROM inpatient_records ir
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors d ON ir.doctor_id = d.doctor_id
            JOIN nurses n ON ir.nurse_id = n.nurse_id
            ORDER BY ir.record_id DESC
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, record_id):
        sql = """
            SELECT ir.*, p.name AS patient_name, p.gender AS patient_gender,
                   p.age AS patient_age, b.bed_no, w.ward_name,
                   d.name AS doctor_name, n.name AS nurse_name,
                   w.price_per_day
            FROM inpatient_records ir
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors d ON ir.doctor_id = d.doctor_id
            JOIN nurses n ON ir.nurse_id = n.nurse_id
            WHERE ir.record_id = %s
        """
        return db.execute_query(sql, (record_id,), fetch_one=True)

    @classmethod
    def get_current_inpatients(cls):
        """获取当前在院患者（使用视图）"""
        sql = "SELECT * FROM v_current_inpatients"
        return db.execute_query(sql)

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT ir.*, p.name AS patient_name, p.gender AS patient_gender,
                   p.age AS patient_age, b.bed_no, w.ward_name,
                   d.name AS doctor_name, n.name AS nurse_name
            FROM inpatient_records ir
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors d ON ir.doctor_id = d.doctor_id
            JOIN nurses n ON ir.nurse_id = n.nurse_id
            WHERE p.name LIKE %s OR w.ward_name LIKE %s
            ORDER BY ir.record_id DESC
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO inpatient_records (patient_id, bed_id, doctor_id, "
               "nurse_id, admit_date, admit_diagnosis, deposit) "
               "VALUES (%(patient_id)s, %(bed_id)s, %(doctor_id)s, "
               "%(nurse_id)s, %(admit_date)s, %(admit_diagnosis)s, %(deposit)s)")
        return db.execute_update(sql, data)

    @classmethod
    def discharge(cls, record_id, discharge_diagnosis=""):
        """办理出院"""
        sql = ("UPDATE inpatient_records SET status='已出院', "
               "discharge_date=NOW(), discharge_diagnosis=%s "
               "WHERE record_id=%s AND status='在院'")
        return db.execute_update(sql, (discharge_diagnosis, record_id))

    @classmethod
    def transfer_bed(cls, record_id, new_bed_id):
        """转床"""
        conn = db.connect()
        cursor = conn.cursor()
        try:
            # 1. 释放旧病床
            cursor.execute(
                "SELECT bed_id FROM inpatient_records WHERE record_id = %s AND status = '在院'",
                (record_id,))
            old = cursor.fetchone()
            if not old:
                raise ValueError("未找到该住院记录或患者已出院")

            # 2. 更新住院记录中的病床
            cursor.execute(
                "UPDATE inpatient_records SET bed_id = %s WHERE record_id = %s",
                (new_bed_id, record_id))

            # 3. 更新旧病床状态
            cursor.execute(
                "UPDATE beds SET status = '清洁中' WHERE bed_id = %s", (old[0],))

            # 4. 更新新病床状态
            cursor.execute(
                "UPDATE beds SET status = '已占用' WHERE bed_id = %s", (new_bed_id,))

            conn.commit()
            return cursor.lastrowid, cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"转床失败: {e}")
        finally:
            cursor.close()

    @classmethod
    def admit_with_procedure(cls, data):
        """使用存储过程一键入院"""
        return db.call_procedure("sp_admit_patient", (
            data["name"], data["gender"], data["age"],
            data.get("id_card", ""), data.get("phone", ""),
            data.get("address", ""), data.get("blood_type", ""),
            data.get("allergy_history", ""),
            data["bed_id"], data["doctor_id"], data["nurse_id"],
            data.get("admit_diagnosis", ""), data.get("deposit", 0)
        ))
