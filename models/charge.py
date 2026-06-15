# models/charge.py
from db.connection import db


class ChargeModel:
    """费用表 CRUD"""

    TABLE = "charges"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT c.*, p.name AS patient_name, w.ward_name, b.bed_no
            FROM charges c
            JOIN inpatient_records ir ON c.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            ORDER BY c.charge_date DESC
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, charge_id):
        sql = """
            SELECT c.*, p.name AS patient_name, w.ward_name, b.bed_no
            FROM charges c
            JOIN inpatient_records ir ON c.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            WHERE c.charge_id = %s
        """
        return db.execute_query(sql, (charge_id,), fetch_one=True)

    @classmethod
    def get_by_record(cls, record_id):
        sql = """
            SELECT c.*, p.name AS patient_name
            FROM charges c
            JOIN inpatient_records ir ON c.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            WHERE c.record_id = %s
            ORDER BY c.charge_date DESC
        """
        return db.execute_query(sql, (record_id,))

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT c.*, p.name AS patient_name, w.ward_name, b.bed_no
            FROM charges c
            JOIN inpatient_records ir ON c.record_id = ir.record_id
            JOIN patients p ON ir.patient_id = p.patient_id
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            WHERE p.name LIKE %s
            ORDER BY c.charge_date DESC
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw,))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO charges (record_id, charge_type, amount, remark) "
               "VALUES (%(record_id)s, %(charge_type)s, %(amount)s, %(remark)s)")
        return db.execute_update(sql, data)

    @classmethod
    def get_revenue_statistics(cls, start_date, end_date):
        """调用存储过程统计收入"""
        return db.call_procedure("sp_daily_revenue", (start_date, end_date))

    @classmethod
    def get_daily_bed_charges(cls, record_id):
        sql = "SELECT * FROM daily_bed_charges WHERE record_id = %s ORDER BY charge_date"
        return db.execute_query(sql, (record_id,))

    @classmethod
    def add_daily_bed_charge(cls, record_id):
        """手动为某在院患者生成当日床位费"""
        sql = """
            INSERT INTO daily_bed_charges (record_id, charge_date, amount)
            SELECT %s, CURDATE(), w.price_per_day
            FROM inpatient_records ir
            JOIN beds b ON ir.bed_id = b.bed_id
            JOIN wards w ON b.ward_id = w.ward_id
            WHERE ir.record_id = %s AND ir.status = '在院'
        """
        return db.execute_update(sql, (record_id, record_id))
