SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+08:00";

CREATE DATABASE IF NOT EXISTS `drivewhereDB` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `drivewhereDB`;

-- error table
DROP TABLE IF EXISTS `error`;
CREATE TABLE IF NOT EXISTS `error` (
  `error_id` int(11) NOT NULL AUTO_INCREMENT,
  `code` int(3) NOT NULL,
  `message` varchar(255) NOT NULL,
  `service` varchar(32) NOT NULL,
  `date_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`error_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- payment table
DROP TABLE IF EXISTS `payment`;
CREATE TABLE IF NOT EXISTS `payment` (
  `paymentId` int(11) NOT NULL AUTO_INCREMENT,
  `rentalId` varchar(32) NOT NULL,
  `payerId` varchar(32) NOT NULL,
  `payeeId` varchar(32) NOT NULL,
  `amountSgd` decimal(10, 2) NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'renting',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`paymentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- rental table & cars
DROP TABLE IF EXISTS `rental`;
CREATE TABLE IF NOT EXISTS `rental` (
  `rentalId` INT NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL,
  `userId` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `carModel` varchar(255) NOT NULL,
  `carMake` varchar(255) NOT NULL,
  `capacity` INT NOT NULL,
  `carPlate` varchar(16) NOT NULL,
  `pricePerDay` decimal(10, 2) NOT NULL,
  PRIMARY KEY (`rentalId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `rental` (`rentalId`, `status`, `userId`, `address`, `carModel`,`carMake`,`capacity`,`carPlate`,`pricePerDay`) VALUES
(1, 'open', '2', '520709', 'Honda', 'HondaWow', 1, '12345678', 10.5),
(2, 'open', '3', '199018', 'Ford Mustang', 'Ford Mustang', 2, '12345678', 10),
(3, 'open', '4', '808932', 'Toyota Camry', 'Toyota Camry', 3, '12345678', 217),
(4, 'open', '5', '138756', 'Chevrolet Silverado', 'Chevrolet Silverado', 4, '12345678', 34),
(5, 'open', '6', '079027', 'BMW 3 Series', 'BMW 3 Series', 5, '12345678', 109),
(6, 'open', '7', '199018', 'Mercedes-Benz C-Class', 'Mercedes-Benz C-Class', 6, '12345678', 14),
(7, 'open', '8', '522201', 'Tesla Model S', 'Tesla Model S', 7, '12345678', 76),
(8, 'open', '9', '600348', 'Audi Q5', 'Audi Q5', 4, '12345678', 321),
(9, 'open', '10', '039594', 'Subaru Outback', 'Subaru Outback', 8, '12345678', 123),
(10, 'open', '11', '069045', 'Jeep Wrangler', 'Jeep Wrangler', 10, '12345678', 420),
(11, 'open', '12', '455286', 'Hyundai Sonata', 'Hyundai Sonata', 11, '12345678', 5.5),
(12, 'open', '13', '507097', 'Nissan Rogue', 'Nissan Rogue', 13, '12345678', 36),
(13, 'open', '14', '188065', 'Kia Sorento', 'Kia Sorento', 6, '12345678', 50),
(14, 'close', '15', '520708', 'Lexus RX', 'Lexus RX', 3, '12345678', 100.5),
(15, 'close', '16', '520707', 'Porsche 911', 'Porsche 911', 1, '12345678', 8.5),
(16, 'close', '17', '520706', 'Honda', 'HondaWow', 1, '12345678', 69);

-- user table | IMPORTANT FOR GRADER: add your own email address, everything can be the same
DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (

  `userId` INT NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `emailAddress` varchar(64) NOT NULL,
  `phoneNum` varchar(64) DEFAULT NULL,
  `stripeId` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`userId`),
  UNIQUE (emailAddress)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `user` (`userId`, `name`, `emailAddress`, `phoneNum`, `stripeId`) VALUES
(1, 'Clement', 'clement@gmail.com', '92882404', 'acct_1OuWDc2MktsaBBhJ'),
(2, 'renter', 'renters@gmail.com', '92436688', 'acct_1OuWDc2MktsaBBhJ');
-- (3, 'grader', '<your email address>', '92436688', 'acct_1OuWDc2MktsaBBhJ');