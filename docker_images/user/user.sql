CREATE DATABASE IF NOT EXISTS `user` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `user`;

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
(2, 'Clement', 'clement@gmail.com', '92882404', 'acct_1OuWDc2MktsaBBhJ'),
(1, 'renter', 'renters@gmail.com', '92436688', 'acct_1OuWDc2MktsaBBhJ');