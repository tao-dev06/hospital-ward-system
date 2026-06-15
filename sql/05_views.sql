-- ============================================================
-- 医院病房管理系统 - 视图脚本（共3个）
-- ============================================================

USE hospital_ward_system;

-- ============================================================
-- 视图1: 当前在院患者完整信息
-- ============================================================
DROP VIEW IF EXISTS v_current_inpatients;
CREATE VIEW v_current_inpatients AS
SELECT
    ir.record_id,
    p.patient_id,
    p.name        AS patient_name,
    p.gender      AS patient_gender,
    p.age         AS patient_age,
    p.id_card,
    p.phone       AS patient_phone,
    w.ward_name,
    w.ward_type,
    b.bed_no,
    b.bed_type,
    d.name        AS doctor_name,
    d.title       AS doctor_title,
    n.name        AS nurse_name,
    ir.admit_date,
    ir.admit_diagnosis,
    ir.deposit,
    DATEDIFF(CURDATE(), ir.admit_date) AS days_in_hospital,
    ir.status
FROM inpatient_records ir
JOIN patients p  ON ir.patient_id = p.patient_id
JOIN beds b      ON ir.bed_id = b.bed_id
JOIN wards w     ON b.ward_id = w.ward_id
JOIN doctors d   ON ir.doctor_id = d.doctor_id
JOIN nurses n    ON ir.nurse_id = n.nurse_id
WHERE ir.status = '在院';

-- ============================================================
-- 视图2: 全院病床状态一览
-- ============================================================
DROP VIEW IF EXISTS v_bed_status;
CREATE VIEW v_bed_status AS
SELECT
    d.dept_name,
    w.ward_name,
    w.ward_type,
    b.bed_no,
    b.bed_type,
    b.status      AS bed_status,
    CASE
        WHEN b.status = '已占用' THEN p.name
        ELSE NULL
    END           AS occupied_by,
    CASE
        WHEN b.status = '已占用' THEN ir.admit_date
        ELSE NULL
    END           AS occupy_since
FROM beds b
JOIN wards w     ON b.ward_id = w.ward_id
JOIN departments d ON w.dept_id = d.dept_id
LEFT JOIN inpatient_records ir ON b.bed_id = ir.bed_id AND ir.status = '在院'
LEFT JOIN patients p ON ir.patient_id = p.patient_id
ORDER BY d.dept_name, w.ward_name, b.bed_no;

-- ============================================================
-- 视图3: 医嘱执行情况
-- ============================================================
DROP VIEW IF EXISTS v_order_execution;
CREATE VIEW v_order_execution AS
SELECT
    mo.order_id,
    p.name          AS patient_name,
    w.ward_name,
    b.bed_no,
    mo.order_type,
    mo.order_content,
    mo.dosage,
    doc.name        AS doctor_name,
    nur.name        AS nurse_name,
    mo.status,
    mo.create_time,
    mo.execute_time,
    mo.fee,
    TIMESTAMPDIFF(MINUTE, mo.create_time, mo.execute_time) AS execute_minutes
FROM medical_orders mo
JOIN inpatient_records ir ON mo.record_id = ir.record_id
JOIN patients p  ON ir.patient_id = p.patient_id
JOIN beds b      ON ir.bed_id = b.bed_id
JOIN wards w     ON b.ward_id = w.ward_id
JOIN doctors doc ON mo.doctor_id = doc.doctor_id
LEFT JOIN nurses nur ON mo.nurse_id = nur.nurse_id
ORDER BY mo.create_time DESC;
