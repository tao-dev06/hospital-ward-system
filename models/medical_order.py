# models/medical_order.py
from db.connection import db


class MedicalOrderModel:
    """医嘱表 CRUD"""

    TABLE = "medical_orders"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT mo.*, p.name AS patient_name, w.ward_name, b.bed_no,
                   doc.name AS doctor_name, nur.name AS nurse_name
            FROM medical_orders mo
            JOIN inpatient_records ir ON mo.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors doc ON mo.doctor_id = doc.doctor_id
            LEFT JOIN nurses nur ON mo.nurse_id = nur.nurse_id
            ORDER BY mo.create_time DESC
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, order_id):
        sql = """
            SELECT mo.*, p.name AS patient_name, w.ward_name, b.bed_no,
                   doc.name AS doctor_name, nur.name AS nurse_name
            FROM medical_orders mo
            JOIN inpatient_records ir ON mo.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors doc ON mo.doctor_id = doc.doctor_id
            LEFT JOIN nurses nur ON mo.nurse_id = nur.nurse_id
            WHERE mo.order_id = %s
        """
        return db.execute_query(sql, (order_id,), fetch_one=True)

    @classmethod
    def get_by_record(cls, record_id):
        sql = """
            SELECT mo.*, doc.name AS doctor_name, nur.name AS nurse_name
            FROM medical_orders mo
            JOIN doctors doc ON mo.doctor_id = doc.doctor_id
            LEFT JOIN nurses nur ON mo.nurse_id = nur.nurse_id
            WHERE mo.record_id = %s
            ORDER BY mo.create_time DESC
        """
        return db.execute_query(sql, (record_id,))

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT mo.*, p.name AS patient_name, w.ward_name, b.bed_no,
                   doc.name AS doctor_name, nur.name AS nurse_name
            FROM medical_orders mo
            JOIN inpatient_records ir ON mo.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN doctors doc ON mo.doctor_id = doc.doctor_id
            LEFT JOIN nurses nur ON mo.nurse_id = nur.nurse_id
            WHERE p.name LIKE %s OR mo.order_content LIKE %s
            ORDER BY mo.create_time DESC
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO medical_orders (record_id, doctor_id, "
               "nurse_id, order_type, order_content, dosage, fee) "
               "VALUES (%(record_id)s, %(doctor_id)s, %(nurse_id)s, "
               "%(order_type)s, %(order_content)s, %(dosage)s, %(fee)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE medical_orders SET record_id=%(record_id)s, "
               "doctor_id=%(doctor_id)s, nurse_id=%(nurse_id)s, "
               "order_type=%(order_type)s, order_content=%(order_content)s, "
               "dosage=%(dosage)s, fee=%(fee)s "
               "WHERE order_id=%(order_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def set_status(cls, order_id, status, nurse_id=None):
        """更新医嘱状态（触发器会自动处理费用）"""
        if status == '已执行':
            sql = ("UPDATE medical_orders SET status=%s, execute_time=NOW(), nurse_id=%s "
                   "WHERE order_id=%s")
            return db.execute_update(sql, (status, nurse_id, order_id))
        else:
            sql = "UPDATE medical_orders SET status=%s WHERE order_id=%s"
            return db.execute_update(sql, (status, order_id))

    @classmethod
    def delete(cls, order_id):
        sql = "DELETE FROM medical_orders WHERE order_id = %s"
        return db.execute_update(sql, (order_id,))
