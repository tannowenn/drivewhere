SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+08:00";

--
-- Database: `payment`
--
CREATE DATABASE IF NOT EXISTS `payment` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `payment`;

-- --------------------------------------------------------

--
-- Table structure for table `payment_record`
--

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

--
-- Dumping data for table `order`
--

-- INSERT INTO `order` (`order_id`, `customer_id`, `status`, `created`, `modified`) VALUES
-- (1, 'Apple TAN', 'NEW', '2020-06-12 02:14:55', '2020-06-12 02:14:55');

COMMIT;
