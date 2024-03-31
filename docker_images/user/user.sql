CREATE DATABASE IF NOT EXISTS `user` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `user`;

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
(3, 'Ryan', 'ryan.ng249@yahoo.com.sg', '91234567', 'acct_1OuWDc2MktsaBBhJ'),
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