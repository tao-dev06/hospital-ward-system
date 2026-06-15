# models/department.py
from db.connection import db


class DepartmentModel:
    """科室表 CRUD"""

    TABLE = "departments"

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM departments ORDER BY dept_id"
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, dept_id):
        sql = "SELECT * FROM departments WHERE dept_id = %s"
        return db.execute_query(sql, (dept_id,), fetch_one=True)

    @classmethod
    def search(cls, keyword):
        sql = ("SELECT * FROM departments WHERE dept_name LIKE %s "
               "OR dept_head LIKE %s ORDER BY dept_id")
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO departments (dept_name, dept_head, phone, floor) "
               "VALUES (%(dept_name)s, %(dept_head)s, %(phone)s, %(floor)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE departments SET dept_name=%(dept_name)s, "
               "dept_head=%(dept_head)s, phone=%(phone)s, floor=%(floor)s "
               "WHERE dept_id=%(dept_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def delete(cls, dept_id):
        sql = "DELETE FROM departments WHERE dept_id = %s"
        return db.execute_update(sql, (dept_id,))
