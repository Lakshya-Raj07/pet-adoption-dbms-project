/* backend/db/procedures.sql */
USE `pet_adoption_db`;

/* --- Procedure 1: CreateAdoption (Transaction) --- */
DROP PROCEDURE IF EXISTS `CreateAdoption`;
DELIMITER $$
CREATE PROCEDURE `CreateAdoption` (
    IN p_animal_id INT,
    IN p_adopter_id INT,
    IN p_employee_id INT
)
BEGIN
    DECLARE animal_current_status VARCHAR(20);

    /* Error handling */
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Adoption failed. Transaction rolled back.';
    END;

    /* Check karo ki animal 'Available' hai ya nahi */
    SELECT `status` INTO animal_current_status
    FROM `Animal`
    WHERE `animal_id` = p_animal_id;

    IF animal_current_status != 'Available' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: This animal is not available for adoption.';
    ELSE
        START TRANSACTION;

        /* 1. Adoption table mein record daalo */
        INSERT INTO `Adoption` (`animal_id`, `adopter_id`, `employee_id`, `adoption_date`)
        VALUES (p_animal_id, p_adopter_id, p_employee_id, CURDATE());
        
        /* 2. Animal ka status 'Adopted' update karo */
        /* Yeh 'after_animal_update_status' trigger ko fire karega */
        UPDATE `Animal`
        SET `status` = 'Adopted'
        WHERE `animal_id` = p_animal_id;

        /* 3. Adoption record ko SELECT karo (API response ke liye) */
        SELECT * FROM `Adoption` 
        WHERE `adoption_id` = LAST_INSERT_ID();

        COMMIT;
    END IF;

END$$
DELIMITER ;


/* --- Procedure 2: CreateAdopter (Transaction) --- */
DROP PROCEDURE IF EXISTS `CreateAdopter`;
DELIMITER $$
CREATE PROCEDURE `CreateAdopter` (
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(20)
)
BEGIN
    DECLARE new_customer_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Failed to create adopter. Transaction rolled back.';
    END;

    START TRANSACTION;

    INSERT INTO `Customer` (`first_name`, `last_name`, `phone`)
    VALUES (p_first_name, p_last_name, p_phone);

    SET new_customer_id = LAST_INSERT_ID();

    INSERT INTO `Adopter` (`customer_id`)
    VALUES (new_customer_id);

    /* Naya record SELECT karo (API response ke liye) */
    SELECT 
        c.customer_id, c.first_name, c.last_name, c.phone, a.adopter_id 
    FROM `Customer` c
    JOIN `Adopter` a ON c.customer_id = a.customer_id
    WHERE c.customer_id = new_customer_id;

    COMMIT;
END$$
DELIMITER ;


/* --- Procedure 3: CreateDonor (Transaction) --- */
DROP PROCEDURE IF EXISTS `CreateDonor`;
DELIMITER $$
CREATE PROCEDURE `CreateDonor` (
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_amount DECIMAL(10, 2)
)
BEGIN
    DECLARE new_customer_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Failed to create donor. Transaction rolled back.';
    END;

    START TRANSACTION;

    INSERT INTO `Customer` (`first_name`, `last_name`, `phone`)
    VALUES (p_first_name, p_last_name, p_phone);

    SET new_customer_id = LAST_INSERT_ID();

    INSERT INTO `Donor` (`customer_id`, `amount`)
    VALUES (new_customer_id, p_amount);

    /* Naya record SELECT karo (API response ke liye) */
    SELECT 
        c.customer_id, c.first_name, c.last_name, c.phone, d.donor_id, d.amount
    FROM `Customer` c
    JOIN `Donor` d ON c.customer_id = d.customer_id
    WHERE c.customer_id = new_customer_id;

    COMMIT;
END$$
DELIMITER ;