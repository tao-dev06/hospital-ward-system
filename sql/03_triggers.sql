-- ============================================================
-- 医院病房管理系统 - 触发器脚本（共6个）
-- ============================================================

USE hospital_ward_system;

-- ============================================================
-- 触发器1: 患者入院时自动将病床状态设为"已占用"
-- ============================================================
DROP TRIGGER IF EXISTS trg_admit_patient;
DELIMITER //
CREATE TRIGGER trg_admit_patient
AFTER INSERT ON inpatient_records
FOR EACH ROW
BEGIN
    -- 仅在状态为"在院"时更新病床状态
    IF NEW.status = '在院' THEN
        UPDATE beds SET status = '已占用' WHERE bed_id = NEW.bed_id;
    END IF;
END//
DELIMITER ;

-- ============================================================
-- 触发器2: 患者出院时将病床状态设为"清洁中"
-- ============================================================
DROP TRIGGER IF EXISTS trg_discharge_patient;
DELIMITER //
CREATE TRIGGER trg_discharge_patient
AFTER UPDATE ON inpatient_records
FOR EACH ROW
BEGIN
    -- 当住院状态从"在院"变为"已出院"时
    IF NEW.status = '已出院' AND OLD.status = '在院' THEN
        UPDATE beds SET status = '清洁中' WHERE bed_id = NEW.bed_id;
    END IF;
END//
DELIMITER ;

-- ============================================================
-- 触发器3: 医嘱执行后自动将费用插入 charges 表
-- ============================================================
DROP TRIGGER IF EXISTS trg_order_fee;
DELIMITER //
CREATE TRIGGER trg_order_fee
AFTER UPDATE ON medical_orders
FOR EACH ROW
BEGIN
    -- 当医嘱状态变为"已执行"且费用大于0时自动插入费用记录
    IF NEW.status = '已执行' AND OLD.status != '已执行' AND NEW.fee > 0 THEN
        INSERT INTO charges(record_id, charge_type, amount, remark)
        VALUES (
            NEW.record_id,
            CASE NEW.order_type
                WHEN '药品' THEN '药费'
                WHEN '检查' THEN '检查费'
                WHEN '护理' THEN '护理费'
                WHEN '手术' THEN '手术费'
                ELSE '其他'
            END,
            NEW.fee,
            CONCAT('医嘱ID:', NEW.order_id, ' ', NEW.order_content)
        );
    END IF;
END//
DELIMITER ;

-- ============================================================
-- 触发器4: 每日床位费插入后同步到 charges 表
-- ============================================================
DROP TRIGGER IF EXISTS trg_daily_bed_fee;
DELIMITER //
CREATE TRIGGER trg_daily_bed_fee
AFTER INSERT ON daily_bed_charges
FOR EACH ROW
BEGIN
    -- 同步到 charges 表，标记为床位费
    INSERT INTO charges(record_id, charge_type, amount, charge_date, remark)
    VALUES (
        NEW.record_id,
        '床位费',
        NEW.amount,
        NOW(),
        CONCAT('床位费 - ', NEW.charge_date)
    );
END//
DELIMITER ;

-- ============================================================
-- 触发器5: 防止将患者分配到已被占用的病床
-- ============================================================
DROP TRIGGER IF EXISTS trg_prevent_occupied_bed;
DELIMITER //
CREATE TRIGGER trg_prevent_occupied_bed
BEFORE INSERT ON inpatient_records
FOR EACH ROW
BEGIN
    DECLARE bed_status VARCHAR(10);
    -- 获取目标病床的状态
    SELECT status INTO bed_status FROM beds WHERE bed_id = NEW.bed_id;
    -- 如果病床已被占用，则阻止插入
    IF bed_status = '已占用' AND NEW.status = '在院' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '该病床已被占用，无法分配！';
    END IF;
END//
DELIMITER ;

-- ============================================================
-- 触发器6: 病床状态变为"维修中"时检查是否有患者占用
-- ============================================================
DROP TRIGGER IF EXISTS trg_update_bed_status;
DELIMITER //
CREATE TRIGGER trg_update_bed_status
BEFORE UPDATE ON beds
FOR EACH ROW
BEGIN
    DECLARE patient_count INT;
    -- 如果要将状态设为"维修中"，检查是否有在院患者占用
    IF NEW.status = '维修中' AND OLD.status = '已占用' THEN
        SELECT COUNT(*) INTO patient_count
        FROM inpatient_records
        WHERE bed_id = NEW.bed_id AND status = '在院';
        IF patient_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = '该病床当前有患者占用，不能设为维修中！请先将患者转床或出院。';
        END IF;
    END IF;
END//
DELIMITER ;
