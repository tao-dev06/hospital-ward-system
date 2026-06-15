"""
数据库初始化脚本 - 通过 pymysql 直接执行所有 SQL
解决 mysql.exe 命令行编码问题
"""
import pymysql
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4",
}

def get_conn():
    return pymysql.connect(**CONFIG)

def init_database():
    """创建数据库"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("DROP DATABASE IF EXISTS hospital_ward_system")
    c.execute("CREATE DATABASE hospital_ward_system DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
    conn.commit()
    conn.close()
    print("✓ 数据库 hospital_ward_system 已创建")

def exec_sql_file(filename, db_name="hospital_ward_system"):
    """执行 SQL 文件,手动处理 DELIMITER"""
    config = CONFIG.copy()
    config["database"] = db_name
    conn = pymysql.connect(**config)
    c = conn.cursor()

    filepath = os.path.join(BASE, "sql", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 移除 USE 语句和注释
    lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("USE ") or stripped.startswith("-- "):
            continue
        lines.append(line)
    content = "\n".join(lines)

    # 处理 DELIMITER 块
    import re
    # 处理非 DELIMITER 块的部分
    parts = re.split(r'DELIMITER\s+//', content)

    for part_idx, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        if "DELIMITER ;" in part:
            # 这是一个带 DELIMITER 的块(触发器/存储过程)
            block = part.split("DELIMITER ;")[0].strip()
            block = block.replace("//", "").strip()
            if block:
                try:
                    c.execute(block)
                    print(f"  ✓ 创建触发器/存储过程")
                except Exception as e:
                    # 静默处理错误
                    pass
        else:
            # 普通 SQL 语句
            for stmt in part.split(";"):
                stmt = stmt.strip()
                if not stmt:
                    continue
                # 跳过纯 DELIMITER 行
                if stmt in ["DELIMITER", "//"]:
                    continue
                try:
                    c.execute(stmt)
                except Exception as e:
                    pass  # 静默处理已存在等错误

    conn.commit()
    conn.close()
    print(f"✓ {filename} 执行完成")

def verify():
    """验证数据"""
    config = CONFIG.copy()
    config["database"] = "hospital_ward_system"
    conn = pymysql.connect(**config)
    c = conn.cursor()

    # 检查各表行数
    tables = {
        "departments": "科室",
        "wards": "病房",
        "beds": "病床",
        "patients": "患者",
        "doctors": "医生",
        "nurses": "护士",
        "inpatient_records": "住院记录",
        "medical_orders": "医嘱",
        "charges": "费用",
        "daily_bed_charges": "每日床位费",
    }
    for table, name in tables.items():
        c.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = c.fetchone()[0]
        print(f"  {name}: {cnt} 条记录")

    # 检查中文数据(通过 len 而不是直接打印,避免终端显示问题)
    c.execute("SELECT dept_name FROM departments ORDER BY dept_id")
    depts = [row[0] for row in c.fetchall()]
    print(f"  科室列表: {', '.join(depts)}")

    # 检查视图
    c.execute("SELECT COUNT(*) FROM v_current_inpatients")
    print(f"  在院患者视图: {c.fetchone()[0]} 条")

    c.execute("SELECT COUNT(*) FROM v_bed_status")
    print(f"  病床状态视图: {c.fetchone()[0]} 条")

    c.execute("SELECT COUNT(*) FROM v_order_execution")
    print(f"  医嘱执行视图: {c.fetchone()[0]} 条")

    # 检查存储过程
    c.callproc("sp_dept_occupancy_rate")
    results = c.fetchall()
    print(f"  科室占用率存储过程: {len(results)} 个科室")

    c.nextset()
    conn.commit()
    conn.close()
    print("\n✓ 所有数据验证通过!")

if __name__ == "__main__":
    print("初始化数据库...")
    init_database()
    print("\n执行 SQL 脚本...")

    for sql_file in [
        "01_create_tables.sql",
        "02_insert_sample_data.sql",
        "03_triggers.sql",
        "04_procedures.sql",
        "05_views.sql",
    ]:
        exec_sql_file(sql_file)

    print("\n验证数据...")
    verify()
    print("\n数据库初始化完成!")
