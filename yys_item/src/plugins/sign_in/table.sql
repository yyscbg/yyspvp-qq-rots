# 用户签到表
CREATE TABLE `user_infos` (
  `qq` varchar(15) NOT NULL,
  `sign_date` varchar(12) DEFAULT NULL COMMENT '签到日期',
  `sign_num` int(11) DEFAULT '0' COMMENT '签到次数',
  `score` int(11) NOT NULL DEFAULT '0' COMMENT '积分',
  `add_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `username` varchar(50) DEFAULT NULL COMMENT '用户名称',
  `vip_expiration` datetime DEFAULT NULL COMMENT 'VIP时效',
  `uuid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`qq`),
  KEY `sign_date` (`sign_date`) USING BTREE,
  KEY `uuid_index` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci



/* 用户收藏链接（价格升降，售卖状态）*/
CREATE TABLE `bookmarks` (
  `user_id` int(12) unsigned NOT NULL COMMENT '用户ID',
  `game_ordersn` varchar(255) NOT NULL COMMENT '收藏链接',
  `first_price` int(11) NOT NULL DEFAULT '0' COMMENT '首次价格',
  `current_price` int(11) NOT NULL DEFAULT '0' COMMENT '当前价格',
  `status_des` int(11) DEFAULT '0' COMMENT '售卖状态',
  `description` text COMMENT '收藏描述',
  `add_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`,`game_ordersn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `all_cbg_url` (
  `game_ordersn` varchar(255) NOT NULL COMMENT '订单号',
  `seller_roleid` varchar(255) DEFAULT '' COMMENT '唯一卖家角色id',
  `equip_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `server_name` varchar(30) DEFAULT '' COMMENT '区服',
  `status_des` int(11) DEFAULT '0' COMMENT '售卖状态',
  `update_time` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  `price` int(11) DEFAULT NULL,
  `create_time` datetime(3) DEFAULT NULL,
  `es_flag` int(11) DEFAULT NULL,
  `new_roleid` varchar(120) DEFAULT NULL,
  `run_date` varchar(12) DEFAULT NULL,
  `uuid_json` json DEFAULT NULL,
  PRIMARY KEY (`game_ordersn`),
  KEY `idx_all_cbg_url_seller__615779` (`seller_roleid`),
  KEY `idx_all_cbg_url_status__c909c9` (`status_des`),
  KEY `idx_all_cbg_url_roleid` (`new_roleid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='all cbg url'
