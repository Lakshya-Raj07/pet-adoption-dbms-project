/* backend/db/triggers.sql */
/*  Redundant 'after_adoption_insert' trigger hata diya hai) */
USE `pet_adoption_db`;

/* --- Trigger 1: Shelter capacity ko update karo (NEW ANIMAL) --- */
/* Yeh trigger tab chalta hai jab naya animal 'Available' status ke saath add hota hai */
DROP TRIGGER IF EXISTS `after_animal_insert`;
DELIMITER $$
CREATE TRIGGER `after_animal_insert`
AFTER INSERT ON `Animal`
FOR EACH ROW
BEGIN
    IF NEW.`status` = 'Available' THEN
        UPDATE `Shelter`
        SET `current_occupancy` = `current_occupancy` + 1
        WHERE `shelter_id` = NEW.`shelter_id`;
    END IF;
END$$
DELIMITER ;


/* --- Trigger 2: Animal status change hone par occupancy update karo --- */
/* YEH SABSE IMPORTANT TRIGGER HAI. YEH ADOPTION AUR CANCELLATION DONO HANDLE KARTA HAI */
DROP TRIGGER IF EXISTS `after_animal_update_status`;
DELIMITER $$
CREATE TRIGGER `after_animal_update_status`
AFTER UPDATE ON `Animal`
FOR EACH ROW
BEGIN
    /* Agar 'Available' se 'Adopted' hua */
    IF OLD.`status` = 'Available' AND NEW.`status` = 'AdoptED' THEN
        UPDATE `Shelter`
        SET `current_occupancy` = `current_occupancy` - 1
        WHERE `shelter_id` = NEW.`shelter_id`;
        
    /* Agar 'Adopted' se 'Available' hua (adoption cancel) */
    ELSEIF OLD.`status` = 'Adopted' AND NEW.`status` = 'Available' THEN
        UPDATE `Shelter`
        SET `current_occupancy` = `current_occupancy` + 1
        WHERE `shelter_id` = NEW.`shelter_id`;
        
    /* Agar 'Available' se 'Pending' hua */
    ELSEIF OLD.`status` = 'Available' AND NEW.`status` = 'Pending' THEN
        UPDATE `Shelter`
        SET `current_occupancy` = `current_occupancy` - 1
        WHERE `shelter_id` = NEW.`shelter_id`;
        
    /* Agar 'Pending' se 'Available' hua (cancel) */
    ELSEIF OLD.`status` = 'Pending' AND NEW.`status` = 'Available' THEN
        UPDATE `Shelter`
        SET `current_occupancy` = `current_occupancy` + 1
        WHERE `shelter_id` = NEW.`shelter_id`;
    END IF;
END$$
DELIMITER ;


/* --- Trigger 3: Shelter ki capacity check karo (BEFORE INSERT) --- */
DROP TRIGGER IF EXISTS `before_animal_insert_check_capacity`;
DELIMITER $$
CREATE TRIGGER `before_animal_insert_check_capacity`
BEFORE INSERT ON `Animal`
FOR EACH ROW
BEGIN
    DECLARE v_current_occupancy INT;
    DECLARE v_capacity INT;
    
    SELECT `current_occupancy`, `capacity`
    INTO v_current_occupancy, v_capacity
    FROM `Shelter`
    WHERE `shelter_id` = NEW.`shelter_id`;
    
    IF v_current_occupancy >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Shelter is full. Cannot add new animal.';
    END IF;
END$$
DELIMITER ;


/* --- Trigger 4: Salary change ko log karo --- */
DROP TRIGGER IF EXISTS `after_employee_salary_update`;
DELIMITER $$
CREATE TRIGGER `after_employee_salary_update`
AFTER UPDATE ON `Employee`
FOR EACH ROW
BEGIN
    IF OLD.`salary` != NEW.`salary` THEN
        INSERT INTO `SalaryChangeLog` (`employee_id`, `old_salary`, `new_salary`)
        VALUES (NEW.`employee_id`, OLD.`salary`, NEW.`salary`);
    END IF;
END$$
DELIMITER ;


/* --- Trigger 5: Shelter ko delete karne se roko --- */
DROP TRIGGER IF EXISTS `before_shelter_delete`;
DELIMITER $$
CREATE TRIGGER `before_shelter_delete`
BEFORE DELETE ON `Shelter`
FOR EACH ROW
BEGIN
    DECLARE employee_count INT;
    
    SELECT COUNT(*) INTO employee_count
    FROM `Employee`
    WHERE `shelter_id` = OLD.`shelter_id`;
    
    IF employee_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Cannot delete shelter. Employees are still assigned.';
    END IF;
END$$
DELIMITER ;


/* --- Trigger 6 & 7: DOB ko future mein hone se roko (ERROR FIX) --- */
DROP TRIGGER IF EXISTS `trg_check_animal_dob_before_insert`;
DELIMITER $$
CREATE TRIGGER `trg_check_animal_dob_before_insert`
BEFORE INSERT ON `Animal`
FOR EACH ROW
BEGIN
    IF NEW.`dob` IS NOT NULL AND NEW.`dob` > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Date of Birth (dob) cannot be in the future.';
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS `trg_check_animal_dob_before_update`;
DELIMITER $$
CREATE TRIGGER `trg_check_animal_dob_before_update`
BEFORE UPDATE ON `Animal`
FOR EACH ROW
BEGIN
    IF NEW.`dob` IS NOT NULL AND NEW.`dob` > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Date of Birth (dob) cannot be in the future.';
    END IF;
END$$
DELIMITER ;