-- ============================================================
-- 医院病房管理系统 - 数据库建表脚本
-- 共 10 张表，包含完整的参照完整性约束
-- ============================================================

CREATE DATABASE IF NOT EXISTS hospital_ward_system
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE hospital_ward_system;

-- ============================================================
-- 表1: departments 科室表
-- ============================================================
CREATE TABLE departments (
    dept_id   INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    dept_head VARCHAR(30),
    phone     VARCHAR(20),
    floor     VARCHAR(10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表2: wards 病房表
-- ============================================================
CREATE TABLE wards (
    ward_id       INT PRIMARY KEY AUTO_INCREMENT,
    ward_name     VARCHAR(30) NOT NULL UNIQUE,
    dept_id       INT NOT NULL,
    ward_type     ENUM('普通病房','ICU','特需病房','隔离病房') NOT NULL DEFAULT '普通病房',
    capacity      INT NOT NULL DEFAULT 4,
    price_per_day DECIMAL(10,2) NOT NULL DEFAULT 100.00,
    CONSTRAINT fk_ward_dept FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表3: beds 病床表
-- ============================================================
CREATE TABLE beds (
    bed_id   INT PRIMARY KEY AUTO_INCREMENT,
    bed_no   VARCHAR(10) NOT NULL,
    ward_id  INT NOT NULL,
    status   ENUM('空闲','已占用','清洁中','维修中') NOT NULL DEFAULT '空闲',
    bed_type ENUM('普通床','升降床','ICU床') NOT NULL DEFAULT '普通床',
    CONSTRAINT fk_bed_ward FOREIGN KEY (ward_id)
        REFERENCES wards(ward_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表4: patients 患者表
-- ============================================================
CREATE TABLE patients (
    patient_id      INT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(30) NOT NULL,
    gender          ENUM('男','女') NOT NULL,
    age             INT,
    id_card         VARCHAR(18) UNIQUE,
    phone           VARCHAR(20),
    address         VARCHAR(200),
    blood_type      VARCHAR(5),
    allergy_history TEXT,
    reg_date        DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表5: doctors 医生表
-- ============================================================
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    name      VARCHAR(30) NOT NULL,
    gender    ENUM('男','女'),
    title     VARCHAR(30),
    dept_id   INT NOT NULL,
    phone     VARCHAR(20),
    specialty VARCHAR(100),
    CONSTRAINT fk_doctor_dept FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表6: nurses 护士表
-- ============================================================
CREATE TABLE nurses (
    nurse_id INT PRIMARY KEY AUTO_INCREMENT,
    name     VARCHAR(30) NOT NULL,
    gender   ENUM('男','女'),
    dept_id  INT NOT NULL,
    phone    VARCHAR(20),
    shift    ENUM('白班','夜班','中班') DEFAULT '白班',
    CONSTRAINT fk_nurse_dept FOREIGN KEY (dept_id)
        REFERENCES departments(dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表7: inpatient_records 住院记录表
-- ============================================================
CREATE TABLE inpatient_records (
    record_id           INT PRIMARY KEY AUTO_INCREMENT,
    patient_id          INT NOT NULL,
    bed_id              INT NOT NULL,
    doctor_id           INT NOT NULL,
    nurse_id            INT NOT NULL,
    admit_date          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    discharge_date      DATETIME,
    admit_diagnosis     VARCHAR(500),
    discharge_diagnosis VARCHAR(500),
    status              ENUM('在院','已出院','转科') NOT NULL DEFAULT '在院',
    deposit             DECIMAL(12,2) DEFAULT 0.00,
    CONSTRAINT fk_inpatient_patient FOREIGN KEY (patient_id)
        REFERENCES patients(patient_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inpatient_bed FOREIGN KEY (bed_id)
        REFERENCES beds(bed_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inpatient_doctor FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inpatient_nurse FOREIGN KEY (nurse_id)
        REFERENCES nurses(nurse_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表8: medical_orders 医嘱表
-- ============================================================
CREATE TABLE medical_orders (
    order_id      INT PRIMARY KEY AUTO_INCREMENT,
    record_id     INT NOT NULL,
    doctor_id     INT NOT NULL,
    nurse_id      INT,
    order_type    ENUM('药品','检查','护理','手术','其他') NOT NULL,
    order_content TEXT NOT NULL,
    dosage        VARCHAR(100),
    create_time   DATETIME DEFAULT CURRENT_TIMESTAMP,
    execute_time  DATETIME,
    status        ENUM('已下达','已审核','已执行','已停止') DEFAULT '已下达',
    fee           DECIMAL(10,2) DEFAULT 0.00,
    CONSTRAINT fk_order_record FOREIGN KEY (record_id)
        REFERENCES inpatient_records(record_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_order_doctor FOREIGN KEY (doctor_id)
        REFERENCES doctors(doctor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_order_nurse FOREIGN KEY (nurse_id)
        REFERENCES nurses(nurse_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表9: charges 费用表
-- ============================================================
CREATE TABLE charges (
    charge_id   INT PRIMARY KEY AUTO_INCREMENT,
    record_id   INT NOT NULL,
    charge_type ENUM('床位费','药费','检查费','护理费','手术费','其他') NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    charge_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    remark      VARCHAR(200),
    CONSTRAINT fk_charge_record FOREIGN KEY (record_id)
        REFERENCES inpatient_records(record_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 表10: daily_bed_charges 每日床位费记录表
-- ============================================================
CREATE TABLE daily_bed_charges (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    record_id   INT NOT NULL,
    charge_date DATE NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    is_paid     TINYINT DEFAULT 0,
    CONSTRAINT fk_daily_record FOREIGN KEY (record_id)
        REFERENCES inpatient_records(record_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
