CREATE TABLE `news_img` (
  `img_id` bigint NOT NULL AUTO_INCREMENT,
  `img_title` varchar(100) DEFAULT NULL COMMENT '图片标题',
  `img_dis` text COMMENT '图片描述',
  `img_url` varchar(100) NOT NULL COMMENT '图片路径',
  PRIMARY KEY (`img_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='新闻图片';

-- test.news_info definition

CREATE TABLE `news_info` (
  `news_id` bigint NOT NULL AUTO_INCREMENT,
  `news_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '新闻内容',
  `user_id` bigint NOT NULL,
  `img_id` bigint DEFAULT NULL,
  PRIMARY KEY (`news_id`),
  KEY `news_info_sys_user_FK` (`user_id`),
  KEY `news_info_news_img_FK` (`img_id`),
  CONSTRAINT `news_info_news_img_FK` FOREIGN KEY (`img_id`) REFERENCES `news_img` (`img_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `news_info_sys_user_FK` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='新闻信息';

-- 菜单 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息', '2000', '1', 'news_info', 'news/news_info/index', 1, 0, 'C', '0', '0', 'news:news_info:list', '#', 'admin', sysdate(), '', null, '新闻信息菜单');

-- 按钮父菜单ID
SELECT @parentId := LAST_INSERT_ID();

-- 按钮 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息查询', @parentId, '1',  '#', '', 1, 0, 'F', '0', '0', 'news:news_info:query',        '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息新增', @parentId, '2',  '#', '', 1, 0, 'F', '0', '0', 'news:news_info:add',          '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息修改', @parentId, '3',  '#', '', 1, 0, 'F', '0', '0', 'news:news_info:edit',         '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息删除', @parentId, '4',  '#', '', 1, 0, 'F', '0', '0', 'news:news_info:remove',       '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻信息导出', @parentId, '5',  '#', '', 1, 0, 'F', '0', '0', 'news:news_info:export',       '#', 'admin', sysdate(), '', null, '');
