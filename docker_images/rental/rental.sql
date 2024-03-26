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

COMMIT;