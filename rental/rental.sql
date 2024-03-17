DROP TABLE IF EXISTS `rental`;
CREATE TABLE IF NOT EXISTS `rental` (
  `rentalId` int NOT NULL AUTO_INCREMENT,
  `status` varchar(16) NOT NULL,
  `userId` int NOT NULL,
  `address` varchar(255) NOT NULL,
  `carModel` varchar(255) NOT NULL,
  `carMake` varchar(255) NOT NULL,
  `capacity` int NOT NULL,
  `carPlate` varchar(16) NOT NULL
  PRIMARY KEY (`rentalId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;