# models/doctor.py
from db.connection import db


class DoctorModel:
    """医生表 CRUD"""

    TABLE = "doctors"

    @classmethod
    def get_all(cls):
        sql = """
            SELECT d.*, dp.dept_name
            FROM doctors d
            JOIN departments dp ON d.dept_id = dp.dept_id
            ORDER BY d.doctor_id
        """
        return db.execute_query(sql)

    @classmethod
    def get_by_id(cls, doctor_id):
        sql = """
            SELECT d.*, dp.dept_name
            FROM doctors d
            JOIN departments dp ON d.dept_id = dp.dept_id
            WHERE d.doctor_id = %s
        """
        return db.execute_query(sql, (doctor_id,), fetch_one=True)

    @classmethod
    def get_by_dept(cls, dept_id):
        sql = """
            SELECT d.*, dp.dept_name
            FROM doctors d
            JOIN departments dp ON d.dept_id = dp.dept_id
            WHERE d.dept_id = %s
            ORDER BY d.doctor_id
        """
        return db.execute_query(sql, (dept_id,))

    @classmethod
    def search(cls, keyword):
        sql = """
            SELECT d.*, dp.dept_name
            FROM doctors d
            JOIN departments dp ON d.dept_id = dp.dept_id
            WHERE d.name LIKE %s OR d.specialty LIKE %s OR dp.dept_name LIKE %s
            ORDER BY d.doctor_id
        """
        kw = f"%{keyword}%"
        return db.execute_query(sql, (kw, kw, kw))

    @classmethod
    def insert(cls, data):
        sql = ("INSERT INTO doctors (name, gender, title, dept_id, phone, specialty) "
               "VALUES (%(name)s, %(gender)s, %(title)s, %(dept_id)s, %(phone)s, %(specialty)s)")
        return db.execute_update(sql, data)

    @classmethod
    def update(cls, data):
        sql = ("UPDATE doctors SET name=%(name)s, gender=%(gender)s, "
               "title=%(title)s, dept_id=%(dept_id)s, phone=%(phone)s, "
               "specialty=%(specialty)s "
               "WHERE doctor_id=%(doctor_id)s")
        return db.execute_update(sql, data)

    @classmethod
    def delete(cls, doctor_id):
        sql = "DELETE FROM doctors WHERE doctor_id = %s"
        return db.execute_update(sql, (doctor_id,))
