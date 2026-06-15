-- ============================================================
-- 医院病房管理系统 - 存储过程脚本（共6个）
-- ============================================================

USE hospital_ward_system;

-- ============================================================
-- 存储过程1: 统计各科室病床占用率
-- ============================================================
DROP PROCEDURE IF EXISTS sp_dept_occupancy_rate;
DELIMITER //
CREATE PROCEDURE sp_dept_occupancy_rate()
BEGIN
    SELECT
        d.dept_id,
        d.dept_name AS 科室名称,
        COUNT(DISTINCT b.bed_id) AS 总床位数,
        COUNT(DISTINCT CASE WHEN b.status = '已占用' THEN b.bed_id END) AS 已占用,
        COUNT(DISTINCT CASE WHEN b.status = '空闲' THEN b.bed_id END) AS 空闲,
        COUNT(DISTINCT CASE WHEN b.status = '维修中' THEN b.bed_id END) AS 维修中,
        ROUND(COUNT(DISTINCT CASE WHEN b.status = '已占用' THEN b.bed_id END) * 100.0 /
              COUNT(DISTINCT b.bed_id), 2) AS 占用率百分比
    FROM departments d
    LEFT JOIN wards w ON d.dept_id = w.dept_id
    LEFT JOIN beds b ON w.ward_id = b.ward_id
    GROUP BY d.dept_id, d.dept_name
    ORDER BY 占用率百分比 DESC;
END//
DELIMITER ;

-- ============================================================
-- 存储过程2: 查询某患者所有住院费用明细和合计
-- ============================================================
DROP PROCEDURE IF EXISTS sp_patient_total_fee;
DELIMITER //
CREATE PROCEDURE sp_patient_total_fee(IN p_patient_id INT)
BEGIN
    DECLARE total_amount DECIMAL(12,2);

    -- 费用明细
    SELECT
        c.charge_id,
        c.charge_type AS 费用类型,
        c.amount AS 金额,
        c.charge_date AS 收费日期,
        c.remark AS 备注,
        ir.record_id AS 住院记录号,
        w.ward_name AS 病房
    FROM charges c
    JOIN inpatient_records ir ON c.record_id = ir.record_id
    JOIN beds b ON ir.bed_id = b.bed_id
    JOIN wards w ON b.ward_id = w.ward_id
    WHERE ir.patient_id = p_patient_id
    ORDER BY c.charge_date DESC;

    -- 费用合计
    SELECT
        COALESCE(SUM(c.amount), 0) INTO total_amount
    FROM charges c
    JOIN inpatient_records ir ON c.record_id = ir.record_id
    WHERE ir.patient_id = p_patient_id;

    SELECT
        p.name AS 患者姓名,
        total_amount AS 总费用,
        COALESCE((SELECT deposit FROM inpatient_records
         WHERE patient_id = p_patient_id ORDER BY record_id DESC LIMIT 1), 0) AS 押金,
        total_amount - COALESCE((SELECT deposit FROM inpatient_records
         WHERE patient_id = p_patient_id ORDER BY record_id DESC LIMIT 1), 0) AS 待缴金额
    FROM patients p
    WHERE p.patient_id = p_patient_id;
END//
DELIMITER ;

-- ============================================================
-- 存储过程3: 统计时间段内医生工作量
-- ============================================================
DROP PROCEDURE IF EXISTS sp_doctor_workload;
DELIMITER //
CREATE PROCEDURE sp_doctor_workload(IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    SELECT
        d.doctor_id,
        d.name AS 医生姓名,
        d.title AS 职称,
        dp.dept_name AS 科室,
        COUNT(DISTINCT ir.record_id) AS 负责患者数,
        COUNT(DISTINCT mo.order_id) AS 下达医嘱数,
        COUNT(DISTINCT CASE WHEN mo.status = '已执行' THEN mo.order_id END) AS 已执行医嘱数
    FROM doctors d
    JOIN departments dp ON d.dept_id = dp.dept_id
    LEFT JOIN inpatient_records ir ON d.doctor_id = ir.doctor_id
        AND ir.admit_date >= p_start_date
        AND ir.admit_date < DATE_ADD(p_end_date, INTERVAL 1 DAY)
    LEFT JOIN medical_orders mo ON d.doctor_id = mo.doctor_id
        AND mo.create_time >= p_start_date
        AND mo.create_time < DATE_ADD(p_end_date, INTERVAL 1 DAY)
    GROUP BY d.doctor_id, d.name, d.title, dp.dept_name
    ORDER BY 下达医嘱数 DESC;
END//
DELIMITER ;

-- ============================================================
-- 存储过程4: 统计各病房使用率
-- ============================================================
DROP PROCEDURE IF EXISTS sp_ward_usage_rate;
DELIMITER //
CREATE PROCEDURE sp_ward_usage_rate()
BEGIN
    SELECT
        w.ward_id,
        w.ward_name AS 病房名称,
        d.dept_name AS 所属科室,
        w.ward_type AS 病房类型,
        w.capacity AS 总床位数,
        COUNT(DISTINCT CASE WHEN b.status = '已占用' THEN b.bed_id END) AS 已占用数,
        COUNT(DISTINCT CASE WHEN b.status = '空闲' THEN b.bed_id END) AS 空闲数,
        ROUND(COUNT(DISTINCT CASE WHEN b.status = '已占用' THEN b.bed_id END) * 100.0 /
              w.capacity, 2) AS 使用率百分比,
        w.price_per_day AS 日床位费
    FROM wards w
    JOIN departments d ON w.dept_id = d.dept_id
    LEFT JOIN beds b ON w.ward_id = b.ward_id
    GROUP BY w.ward_id, w.ward_name, d.dept_name, w.ward_type, w.capacity, w.price_per_day
    ORDER BY 使用率百分比 DESC;
END//
DELIMITER ;

-- ============================================================
-- 存储过程5: 统计时间段内各项收入
-- ============================================================
DROP PROCEDURE IF EXISTS sp_daily_revenue;
DELIMITER //
CREATE PROCEDURE sp_daily_revenue(IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    -- 按费用类型统计
    SELECT
        charge_type AS 费用类型,
        COUNT(*) AS 收费笔数,
        SUM(amount) AS 总金额,
        ROUND(AVG(amount), 2) AS 平均金额
    FROM charges
    WHERE charge_date >= p_start_date
      AND charge_date < DATE_ADD(p_end_date, INTERVAL 1 DAY)
    GROUP BY charge_type
    WITH ROLLUP;

    -- 按日统计
    SELECT
        DATE(charge_date) AS 日期,
        COUNT(*) AS 收费笔数,
        SUM(amount) AS 当日收入
    FROM charges
    WHERE charge_date >= p_start_date
      AND charge_date < DATE_ADD(p_end_date, INTERVAL 1 DAY)
    GROUP BY DATE(charge_date)
    ORDER BY 日期;
END//
DELIMITER ;

-- ============================================================
-- 存储过程6: 一键办理入院
-- ============================================================
DROP PROCEDURE IF EXISTS sp_admit_patient;
DELIMITER //
CREATE PROCEDURE sp_admit_patient(
    IN p_name VARCHAR(30),
    IN p_gender ENUM('男','女'),
    IN p_age INT,
    IN p_id_card VARCHAR(18),
    IN p_phone VARCHAR(20),
    IN p_address VARCHAR(200),
    IN p_blood_type VARCHAR(5),
    IN p_allergy TEXT,
    IN p_bed_id INT,
    IN p_doctor_id INT,
    IN p_nurse_id INT,
    IN p_admit_diagnosis VARCHAR(500),
    IN p_deposit DECIMAL(12,2)
)
BEGIN
    DECLARE v_patient_id INT;
    DECLARE v_record_id INT;
    DECLARE v_bed_status VARCHAR(10);

    -- 开启事务
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '入院办理失败，已回滚！';
    END;

    START TRANSACTION;

    -- 检查病床状态
    SELECT status INTO v_bed_status FROM beds WHERE bed_id = p_bed_id FOR UPDATE;
    IF v_bed_status != '空闲' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '该病床当前不可用！';
    END IF;

    -- 插入患者信息（如果身份证号已存在则使用已有记录）
    IF p_id_card IS NOT NULL AND p_id_card != '' THEN
        SELECT patient_id INTO v_patient_id FROM patients WHERE id_card = p_id_card;
        IF v_patient_id IS NULL THEN
            INSERT INTO patients(name, gender, age, id_card, phone, address, blood_type, allergy_history)
            VALUES(p_name, p_gender, p_age, p_id_card, p_phone, p_address, p_blood_type, p_allergy);
            SET v_patient_id = LAST_INSERT_ID();
        END IF;
    ELSE
        INSERT INTO patients(name, gender, age, phone, address, blood_type, allergy_history)
        VALUES(p_name, p_gender, p_age, p_phone, p_address, p_blood_type, p_allergy);
        SET v_patient_id = LAST_INSERT_ID();
    END IF;

    -- 创建住院记录（触发器会自动更新病床状态）
    INSERT INTO inpatient_records(patient_id, bed_id, doctor_id, nurse_id, admit_diagnosis, deposit)
    VALUES(v_patient_id, p_bed_id, p_doctor_id, p_nurse_id, p_admit_diagnosis, p_deposit);
    SET v_record_id = LAST_INSERT_ID();

    -- 生成当日床位费
    INSERT INTO daily_bed_charges(record_id, charge_date, amount)
    SELECT v_record_id, CURDATE(), w.price_per_day
    FROM beds b JOIN wards w ON b.ward_id = w.ward_id
    WHERE b.bed_id = p_bed_id;

    COMMIT;

    -- 返回结果
    SELECT
        v_patient_id AS 患者编号,
        v_record_id AS 住院记录编号,
        p_name AS 患者姓名,
        '入院成功' AS 状态;
END//
DELIMITER ;
