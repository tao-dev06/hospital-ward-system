# models/bed.py
from db.connection import db


class BedModel:
    """病床表 CRUD"""

    TABLE = "beds"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT b.*, w.ward_name, d.dept_name
            FROM beds b
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN departments d ON w.dept_id = d.dept_id
            ORDER BY d.dept_name, w.ward_name, b.bed_no
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, bed_id):
        sql = """
            SELECT b.*, w.ward_name, d.dept_name, w.price_per_day
            FROM beds b
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN departments d ON w.dept_id = d.dept_id
            WHERE b.bed_id = %s
        """
        return db.execute_query(sql, (bed_id,), fetch_one=True)

    @classmethod
    def get_by_ward(cls, ward_id):
        sql = """
            SELECT b.*, w.ward_name
            FROM beds b
            JOIN wards w ON b.ward_id = w.ward_id
            WHERE b.ward_id = %s
            ORDER BY b.bed_no
        """
        return db.execute_query(sql, (ward_id,))

    @classmethod
    def get_available(cls):
        """获取所有空闲病床"""
        sql = """
            SELECT b.*, w.ward_name, d.dept_name, w.price_per_day
            FROM beds b
            JOIN wards w ON b.ward_id = w.ward_id
            JOIN departments d ON w.dept_id = d.dept_id
            WHERE b.status = '空闲'
            ORDER BY d.dept_name, w.ward_name, b.bed_no
        """
        return db.execute_query(sql)

    @classmethod
    def get_available_by_dept(cls, dept_id):
        """获取指定科室的空闲病床"""
        sql = """
            SELECT b.*, w.ward_name, w.price_per_day
            FROM beds b
            JOIN wards w ON b.ward_id = w.ward_id
            WHERE w.dept_id = %s AND b.status = '空闲'
            ORDER BY w.ward_name, b.bed_no
        """
        return db.execute_query(sql, (dept_id,))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO beds (bed_no, ward_id, status, bed_type) "
               "VALUES (%(bed_no)s, %(ward_id)s, %(status)s, %(bed_type)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE beds SET bed_no=%(bed_no)s, ward_id=%(ward_id)s, "
               "status=%(status)s, bed_type=%(bed_type)s "
               "WHERE bed_id=%(bed_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def update_status(cls, bed_id, status):
        sql = "UPDATE beds SET status = %s WHERE bed_id = %s"
        return db.execute_update(sql, (status, bed_id))

    @classmethod
    def delete(cls, bed_id):
        sql = "DELETE FROM beds WHERE bed_id = %s"
        return db.execute_update(sql, (bed_id,))

    @classmethod
    def bed_status_view(cls):
        """查询全院病床状态视图"""
        sql = "SELECT * FROM v_bed_status"
        return db.execute_query(sql)
