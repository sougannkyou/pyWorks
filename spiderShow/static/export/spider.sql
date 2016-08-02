﻿# Host: 127.0.0.1  (Version 5.6.20)
# Date: 2016-08-02 17:31:32
# Generator: MySQL-Front 5.3  (Build 7.6)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "content_rule"
#

DROP TABLE IF EXISTS `content_rule`;
CREATE TABLE `content_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `list_regex` varchar(255) DEFAULT NULL COMMENT '列表页-正则',
  `regex_or_xpath` char(1) DEFAULT '0' COMMENT '0:xpath, 1:正则',
  `item` varchar(255) NOT NULL DEFAULT 'title' COMMENT 'title，author，ctime，content 等',
  `content_rule` varchar(255) DEFAULT NULL COMMENT '匹配规则',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `item` (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Data for table "content_rule"
#


#
# Structure for table "current_domain_setting"
#

DROP TABLE IF EXISTS `current_domain_setting`;
CREATE TABLE `current_domain_setting` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `black_domain_str` varchar(255) DEFAULT NULL COMMENT '以 ; 分割的列表',
  `setting_json` longtext COMMENT '配置简报，json版',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;

#
# Data for table "current_domain_setting"
#

INSERT INTO `current_domain_setting` VALUES (70,'admin','http://www.ccgp.gov.cn/','ccgp.gov.cn','search.ccgp.gov.cn','');

#
# Structure for table "result_file_list"
#

DROP TABLE IF EXISTS `result_file_list`;
CREATE TABLE `result_file_list` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT '',
  `start_url` varchar(255) NOT NULL DEFAULT '',
  `site_domain` varchar(255) DEFAULT '',
  `result_file` longblob COMMENT '结果文件（.zip）',
  `tmp_path` varchar(255) DEFAULT NULL COMMENT 'DB->文件后的路径',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `user_id` (`user_id`,`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COMMENT='列表页结果-文件形式';

#
# Data for table "result_file_list"
#

#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT 'admin' COMMENT 'user',
  `start_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'homepage',
  `site_domain` varchar(255) NOT NULL DEFAULT '' COMMENT 'domain',
  `black_domain_str` varchar(255) DEFAULT NULL COMMENT 'black_domain_str  <-  ; ; ;',
  `detail_or_list` char(1) DEFAULT '0' COMMENT '0:detail,1:list',
  `scope` char(1) NOT NULL DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `white_or_black` char(1) NOT NULL DEFAULT '0' COMMENT '0:white,1:black',
  `weight` char(1) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `scope` (`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=144 DEFAULT CHARSET=utf8;

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (27,'admin','http://cpt.xtu.edu.cn/','cpt.xtu.edu.cn',NULL,'0','1','0','0','/[a-zA-Z]{1,}/[a-zA-Z]{1,}/d{4}/?d{4}/d{1,}.html',NULL),(28,'admin','http://cpt.xtu.edu.cn/','cpt.xtu.edu.cn',NULL,'0','1','0','0','/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/d{4}/?d{4}/d{1,}.html',NULL),(29,'admin','http://cpt.xtu.edu.cn/','cpt.xtu.edu.cn',NULL,'0','1','0','0','/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/d{4}/?d{4}/d{1,}.html',NULL),(30,'admin','http://cpt.xtu.edu.cn/','cpt.xtu.edu.cn',NULL,'1','1','0','0','list',NULL),(123,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','post-',NULL),(124,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','pic-',NULL),(125,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','compose.jsp',NULL),(126,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','nextid',NULL),(127,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','/$',NULL),(128,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','list',NULL),(129,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','index',NULL),(130,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','hotArticle',NULL),(144,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','0','1','0','0','thread-',NULL),(145,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','1','1','0','0','/$',NULL),(146,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','1','1','0','0','forum',NULL),(167,'admin','http://news.hefei.cc/','news.hefei.cc','','0','1','0','0','/s/',NULL),(168,'admin','http://news.hefei.cc/','news.hefei.cc','','0','1','0','0','/d{4}/d{4}/d{1,}_d{1,}.shtml',NULL),(169,'admin','http://news.hefei.cc/','news.hefei.cc','','0','1','0','0','search.php',NULL),(170,'admin','http://news.hefei.cc/','news.hefei.cc','','0','1','0','0','/d{4}/d{4}/d{1,}.shtml',NULL),(171,'admin','http://news.hefei.cc/','news.hefei.cc','','1','1','0','0','/L/d{1,}.shtml',NULL),(172,'admin','http://news.hefei.cc/','news.hefei.cc','','1','1','0','0','/$',NULL),(173,'admin','http://www.cankaoxiaoxi.com/','cankaoxiaoxi.com','','0','1','0','0','/[a-zA-Z]{1,}/?[a-zA-Z]{1,}/d{4}/?d{4}/d{1,}_?d{1,}.shtml',NULL),(174,'admin','http://www.cankaoxiaoxi.com/','cankaoxiaoxi.com','','0','1','0','0','/d{4}/?d{4}/d{1,}/?d{1,}_?d{1,}.shtml',NULL),(175,'admin','http://www.cankaoxiaoxi.com/','cankaoxiaoxi.com','','1','1','0','0','/$',NULL),(233,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','0','1','0','0','d{1,}_d{1,}_d{1,}_d{1,}.s?html',NULL),(234,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','0','1','0','0','/[a-zA-Z]{1,}/?[a-zA-Z]{1,}/d{1,}[/|_]?d{1,}.s?html',NULL),(235,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','0','1','0','0','detail',NULL),(236,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','0','1','0','0','/a/d{8}/d{1,}_?d{1,}.shtml',NULL),(237,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','1','1','0','0','list',NULL),(238,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','1','1','0','0','index',NULL),(239,'admin','http://news.ifeng.com/','news.ifeng.com','bloghistory.news.ifeng.com','1','1','0','0','/$',NULL),(240,'admin','http://xinwen.eastday.com/','xinwen.eastday.com','','0','1','0','0','d{1,}.shtml',NULL),(241,'admin','http://xinwen.eastday.com/','xinwen.eastday.com','','0','1','0','0','/d{4}/d{4}/d{1,}.shtml',NULL),(242,'admin','http://xinwen.eastday.com/','xinwen.eastday.com','','1','1','0','0','/$',NULL),(243,'admin','http://xinwen.eastday.com/','xinwen.eastday.com','','1','1','0','0','list',NULL),(244,'admin','http://news.iqilu.com/','news.iqilu.com','','0','1','0','0','d{1,}.shtml',NULL),(245,'admin','http://news.iqilu.com/','news.iqilu.com','','0','1','0','0','/d{4}/d{4}/d{1,}.shtml',NULL),(246,'admin','http://news.iqilu.com/','news.iqilu.com','','0','1','0','0','/a/d{1,}.shtml',NULL),(247,'admin','http://news.iqilu.com/','news.iqilu.com','','1','1','0','0','/$',NULL),(248,'admin','http://news.iqilu.com/','news.iqilu.com','','1','1','0','0','list',NULL),(249,'admin','http://www.ccgp.gov.cn/','ccgp.gov.cn','search.ccgp.gov.cn','0','1','0','0','_d{1,}.htm',NULL),(250,'admin','http://www.ccgp.gov.cn/','ccgp.gov.cn','search.ccgp.gov.cn','1','1','0','0','/$',NULL);

#
# Structure for table "user"
#

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `Authorization` char(1) DEFAULT NULL COMMENT '0:admin,1:normal',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

#
# Data for table "user"
#

INSERT INTO `user` VALUES (1,'admin','admin','0','admin'),(2,'user','user','1','normal user');
