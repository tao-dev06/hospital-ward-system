# models/ward.py
from db.connection import db


class WardModel:
    """病房表 CRUD"""

    TABLE = "wards"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT w.*, d.dept_name
            FROM wards w
            JOIN departments d ON w.dept_id = d.dept_id
            ORDER BY w.ward_id
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, ward_id):
        sql = """
            SELECT w.*, d.dept_name
            FROM wards w
            JOIN departments d ON w.dept_id = d.dept_id
            WHERE w.ward_id = %s
        """
        return db.execute_query(sql, (ward_id,), fetch_one=True)

    @classmethod
    def get_by_dept(cls, dept_id):
        sql = "SELECT * FROM wards WHERE dept_id = %s ORDER BY ward_id"
        return db.execute_query(sql, (dept_id,))

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT w.*, d.dept_name
            FROM wards w
            JOIN departments d ON w.dept_id = d.dept_id
            WHERE w.ward_name LIKE %s OR d.dept_name LIKE %s
            ORDER BY w.ward_id
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO wards (ward_name, dept_id, ward_type, capacity, price_per_day) "
               "VALUES (%(ward_name)s, %(dept_id)s, %(ward_type)s, %(capacity)s, %(price_per_day)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE wards SET ward_name=%(ward_name)s, dept_id=%(dept_id)s, "
               "ward_type=%(ward_type)s, capacity=%(capacity)s, "
               "price_per_day=%(price_per_day)s "
               "WHERE ward_id=%(ward_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def delete(cls, ward_id):
        sql = "DELETE FROM wards WHERE ward_id = %s"
        return db.execute_update(sql, (ward_id,))
