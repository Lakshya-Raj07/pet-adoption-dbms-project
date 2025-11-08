/* backend/db/schema.sql */

/* Pehle 'child' tables (jinke paas Foreign Key hai) ko drop karo */
DROP TABLE IF EXISTS `Donation`;
DROP TABLE IF EXISTS `Adoption`;
DROP TABLE IF EXISTS `SalaryChangeLog`; 
DROP TABLE IF EXISTS `Donor`;
DROP TABLE IF EXISTS `Adopter`;
DROP TABLE IF EXISTS `Animal`;
DROP TABLE IF EXISTS `Employee`; 

/* Ab 'parent' tables (jinke paas Foreign Key nahi hai) ko drop karo */
DROP TABLE IF EXISTS `Customer`;
DROP TABLE IF EXISTS `Shelter`;

/* Independent tables */
DROP TABLE IF EXISTS `AuditLog`;


/* Ab tables create karo  */
CREATE TABLE `Shelter` (
  `shelter_id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `address` VARCHAR(255),
  `capacity` INT NOT NULL,
  `current_occupancy` INT NOT NULL DEFAULT 0,
  CONSTRAINT `chk_capacity` CHECK (`capacity` > 0),
  CONSTRAINT `chk_occupancy` CHECK (`current_occupancy` >= 0 AND `current_occupancy` <= `capacity`)
);

CREATE TABLE `Customer` (
  `customer_id` INT AUTO_INCREMENT PRIMARY KEY,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) UNIQUE
);

CREATE TABLE `Employee` (
  `employee_id` INT AUTO_INCREMENT PRIMARY KEY,
  `shelter_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `role` VARCHAR(50),
  `salary` DECIMAL(10, 2),
  FOREIGN KEY (`shelter_id`) REFERENCES `Shelter`(`shelter_id`) ON DELETE SET NULL,
  CONSTRAINT `chk_salary` CHECK (`salary` > 0)
);

CREATE TABLE `Animal` (
  `animal_id` INT AUTO_INCREMENT PRIMARY KEY,
  `shelter_id` INT,
  `name` VARCHAR(100) NOT NULL,
  `species` VARCHAR(50),
  `breed` VARCHAR(50),
  `age` INT,
  `gender` CHAR(1),
  `dob` DATE,
  `status` VARCHAR(20) NOT NULL DEFAULT 'Available',
  FOREIGN KEY (`shelter_id`) REFERENCES `Shelter`(`shelter_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_age` CHECK (`age` >= 0),
  CONSTRAINT `chk_gender` CHECK (`gender` IN ('M', 'F', 'N')),
  CONSTRAINT `chk_status` CHECK (`status` IN ('Available', 'Adopted', 'Pending'))
);

CREATE TABLE `Adopter` (
  `adopter_id` INT AUTO_INCREMENT PRIMARY KEY,
  `customer_id` INT NOT NULL UNIQUE,
  FOREIGN KEY (`customer_id`) REFERENCES `Customer`(`customer_id`) ON DELETE CASCADE
);

CREATE TABLE `Donor` (
  `donor_id` INT AUTO_INCREMENT PRIMARY KEY,
  `customer_id` INT NOT NULL UNIQUE,
  `amount` DECIMAL(10, 2) DEFAULT 0.00,
  FOREIGN KEY (`customer_id`) REFERENCES `Customer`(`customer_id`) ON DELETE CASCADE
);

CREATE TABLE `Adoption` (
  `adoption_id` INT AUTO_INCREMENT PRIMARY KEY,
  `animal_id` INT NOT NULL UNIQUE,
  `adopter_id` INT NOT NULL,
  `employee_id` INT,
  `adoption_date` DATE NOT NULL,
  FOREIGN KEY (`animal_id`) REFERENCES `Animal`(`animal_id`),
  FOREIGN KEY (`adopter_id`) REFERENCES `Adopter`(`adopter_id`),
  FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`employee_id`) ON DELETE SET NULL
);

CREATE TABLE `Donation` (
  `donation_id` INT AUTO_INCREMENT PRIMARY KEY,
  `donor_id` INT NOT NULL,
  `shelter_id` INT,
  `amount` DECIMAL(10, 2) NOT NULL,
  `donation_date` DATE NOT NULL,
  FOREIGN KEY (`donor_id`) REFERENCES `Donor`(`donor_id`),
  FOREIGN KEY (`shelter_id`) REFERENCES `Shelter`(`shelter_id`) ON DELETE SET NULL,
  CONSTRAINT `chk_donation_amount` CHECK (`amount` > 0)
);

CREATE TABLE `AuditLog` (
  `log_id` INT AUTO_INCREMENT PRIMARY KEY,
  `action_type` VARCHAR(50),
  `table_name` VARCHAR(50),
  `record_id` INT,
  `log_message` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `SalaryChangeLog` (
  `log_id` INT AUTO_INCREMENT PRIMARY KEY,
  `employee_id` INT,
  `old_salary` DECIMAL(10, 2),
  `new_salary` DECIMAL(10, 2),
  `changed_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`employee_id`) REFERENCES `Employee`(`employee_id`) ON DELETE CASCADE
);