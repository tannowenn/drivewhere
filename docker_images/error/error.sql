SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


CREATE DATABASE IF NOT EXISTS `error` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `error`;


DROP TABLE IF EXISTS `error`;
CREATE TABLE IF NOT EXISTS `error` (
  `error_id` int(11) NOT NULL AUTO_INCREMENT,
  `code` int(3) NOT NULL,
  `message` varchar(255) NOT NULL,
  `service` varchar(32) NOT NULL,
  `date_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`error_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


INSERT INTO `error` (`error_id`, `code`, `message`, `service`, `date_time`) VALUES
(1, 404, 'There are no listings', 'rental', '2020-06-12 02:14:55');

