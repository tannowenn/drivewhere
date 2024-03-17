-- SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
-- SET AUTOCOMMIT = 0;
-- START TRANSACTION;
-- SET time_zone = "+08:00";

CREATE DATABASE IF NOT EXISTS `rental` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `rental`;

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
  PRIMARY KEY (`rentalId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `rental` (`rentalId`, `status`, `userId`, `address`, `carModel`,`carMake`,`capacity`,`carPlate`) VALUES
(1, 'open', '2', '520709', 'Honda', 'HondaWow', 1, '12345678');