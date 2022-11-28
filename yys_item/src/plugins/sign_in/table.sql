# 用户签到表
CREATE TABLE `user_infos` (
  `id` INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `qq` varchar(15) unique NOT NULL,
  `sign_date` varchar(12) DEFAULT NULL COMMENT "签到日期",
  `sign_num` int DEFAULT 0 COMMENT "签到次数",
  `score` int DEFAULT NULL COMMENT '积分',
  `add_time` timestamp not NULL,
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  KEY `sign_date` (`sign_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4





