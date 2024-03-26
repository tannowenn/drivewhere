DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (

  `userId` INT NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `emailAddress` varchar(64) NOT NULL,
  `phoneNum` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`userId`),
  UNIQUE (emailAddress)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

