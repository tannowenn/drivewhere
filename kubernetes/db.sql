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
(1, 'open', '2', '520709', 'Civic', 'Honda', 1, '12345678', 10.5),
(2, 'open', '3', '199018', 'Mustang', 'Ford', 2, '12345678', 10),
(3, 'open', '4', '808932', 'Camry', 'Toyota', 3, '12345678', 217),
(4, 'open', '5', '138756', 'Silverado', 'Chevrolet', 4, '12345678', 34),
(5, 'open', '6', '079027', '3 Series', 'BMW', 5, '12345678', 109),
(6, 'open', '7', '199018', 'C-Class', 'Mercedes-Benz', 6, '12345678', 14),
(7, 'open', '8', '522201', 'Model S', 'Tesla', 7, '12345678', 76),
(8, 'open', '9', '600348', 'Q5', 'Audi', 4, '12345678', 321),
(9, 'open', '10', '039594', 'Outback', 'Subaru', 8, '12345678', 123),
(10, 'open', '11', '069045', 'Wrangler', 'Jeep', 10, '12345678', 420),
(11, 'open', '12', '455286', 'Sonata', 'Hyundai', 11, '12345678', 5.5),
(12, 'open', '13', '507097', 'Rogue', 'Nissan', 13, '12345678', 36);

-- user table | IMPORTANT FOR GRADER: add your own email address, everything can be the same
DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (

  `userId` INT NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `emailAddress` varchar(64) NOT NULL,
  `phoneNum` varchar(64) DEFAULT NULL,
  `stripeId` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `user` (`userId`, `name`, `emailAddress`, `phoneNum`, `stripeId`) VALUES
(1, 'renter', 'ryan.ng.2022@scis.smu.edu.sg', '92436688', 'acct_1OuWDc2MktsaBBhJ'),
(2, 'Clement', 'ryan.ng.2022@scis.smu.edu.sg', '92882404', 'acct_1OuWDc2MktsaBBhJ'),
(3, 'Ryan', 'brandonlim_99@outlook.com', '91234567', 'acct_1OuWDc2MktsaBBhJ'),
(4, 'Brandon', 'ryan.ng.2022@scis.smu.edu.sg', '98765432', 'acct_1OuWDc2MktsaBBhJ'),
(5, 'Owen', 'ryan.ng.2022@scis.smu.edu.sg', '91231234', 'acct_1OuWDc2MktsaBBhJ'),
(6, 'Elliott', 'ryan.ng.2022@scis.smu.edu.sg', '93213214', 'acct_1OuWDc2MktsaBBhJ'),
(7, 'Bob', 'ryan.ng.2022@scis.smu.edu.sg', '98768761', 'acct_1OuWDc2MktsaBBhJ'),
(8, 'Myat', 'ryan.ng.2022@scis.smu.edu.sg', '96786781', 'acct_1OuWDc2MktsaBBhJ'),
(9, 'Sherine', 'ryan.ng.2022@scis.smu.edu.sg', '91324576', 'acct_1OuWDc2MktsaBBhJ'),
(10, 'Meldrick', 'ryan.ng.2022@scis.smu.edu.sg', '91827364', 'acct_1OuWDc2MktsaBBhJ'),
(11, 'Lee', 'ryan.ng.2022@scis.smu.edu.sg', '94536271', 'acct_1OuWDc2MktsaBBhJ'),
(12, 'Bill', 'ryan.ng.2022@scis.smu.edu.sg', '93321123', 'acct_1OuWDc2MktsaBBhJ'),
(13, 'Beyonce', 'ryan.ng.2022@scis.smu.edu.sg', '94567123', 'acct_1OuWDc2MktsaBBhJ');
