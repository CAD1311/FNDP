-- 菜单 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img', '3', '1', 'img', 'news/img/index', 1, 0, 'C', '0', '0', 'news:img:list', '#', 'admin', sysdate(), '', null, 'news_img菜单');

-- 按钮父菜单ID
SELECT @parentId := LAST_INSERT_ID();

-- 按钮 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img查询', @parentId, '1',  '#', '', 1, 0, 'F', '0', '0', 'news:img:query',        '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img新增', @parentId, '2',  '#', '', 1, 0, 'F', '0', '0', 'news:img:add',          '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img修改', @parentId, '3',  '#', '', 1, 0, 'F', '0', '0', 'news:img:edit',         '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img删除', @parentId, '4',  '#', '', 1, 0, 'F', '0', '0', 'news:img:remove',       '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('news_img导出', @parentId, '5',  '#', '', 1, 0, 'F', '0', '0', 'news:img:export',       '#', 'admin', sysdate(), '', null, '');
