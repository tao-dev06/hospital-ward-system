# db/connection.py
# 数据库连接管理模块
import pymysql
from .config import DB_CONFIG


class Database:
    """数据库连接管理类（单例模式）"""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        """获取数据库连接"""
        try:
            if self._connection is None or not self._connection.open:
                self._connection = pymysql.connect(**DB_CONFIG)
        except Exception as e:
            raise ConnectionError(f"数据库连接失败: {e}")
        return self._connection

    def close(self):
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None

    def commit(self):
        """提交事务"""
        if self._connection and self._connection.open:
            self._connection.commit()

    def rollback(self):
        """回滚事务"""
        if self._connection and self._connection.open:
            self._connection.rollback()

    def execute_query(self, sql, params=None, fetch_one=False):
        """执行查询并返回结果"""
        conn = self.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"查询执行失败: {e}\nSQL: {sql}")
        finally:
            cursor.close()

    def execute_update(self, sql, params=None):
        """执行增删改操作"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.lastrowid, cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"更新执行失败: {e}\nSQL: {sql}")
        finally:
            cursor.close()

    def call_procedure(self, proc_name, args=None):
        """调用存储过程"""
        conn = self.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.callproc(proc_name, args or ())
            # 存储过程可能返回多个结果集
            results = []
            results.append(cursor.fetchall())
            # 处理后续结果集
            while cursor.nextset():
                results.append(cursor.fetchall())
            conn.commit()
            return results
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"存储过程执行失败: {e}")
        finally:
            cursor.close()


# 全局数据库实例
db = Database()
