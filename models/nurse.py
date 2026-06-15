# models/nurse.py
from db.connection import db


class NurseModel:
    """护士表 CRUD"""

    TABLE = "nurses"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT n.*, d.dept_name
            FROM nurses n
            JOIN departments d ON n.dept_id = d.dept_id
            ORDER BY n.nurse_id
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, nurse_id):
        sql = """
            SELECT n.*, d.dept_name
            FROM nurses n
            JOIN departments d ON n.dept_id = d.dept_id
            WHERE n.nurse_id = %s
        """
        return db.execute_query(sql, (nurse_id,), fetch_one=True)

    @classmethod
    def get_by_dept(cls, dept_id):
        sql = """
            SELECT n.*, d.dept_name
            FROM nurses n
            JOIN departments d ON n.dept_id = d.dept_id
            WHERE n.dept_id = %s
            ORDER BY n.nurse_id
        """
        return db.execute_query(sql, (dept_id,))

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT n.*, d.dept_name
            FROM nurses n
            JOIN departments d ON n.dept_id = d.dept_id
            WHERE n.name LIKE %s OR d.dept_name LIKE %s
            ORDER BY n.nurse_id
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO nurses (name, gender, dept_id, phone, shift) "
               "VALUES (%(name)s, %(gender)s, %(dept_id)s, %(phone)s, %(shift)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE nurses SET name=%(name)s, gender=%(gender)s, "
               "dept_id=%(dept_id)s, phone=%(phone)s, shift=%(shift)s "
               "WHERE nurse_id=%(nurse_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def delete(cls, nurse_id):
        sql = "DELETE FROM nurses WHERE nurse_id = %s"
        return db.execute_update(sql, (nurse_id,))
