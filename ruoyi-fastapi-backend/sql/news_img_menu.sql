-- 菜单 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片', '3', '1', 'news_img', 'news/news_img/index', 1, 0, 'C', '0', '0', 'news:news_img:list', '#', 'admin', sysdate(), '', null, '新闻图片菜单');

-- 按钮父菜单ID
SELECT @parentId := LAST_INSERT_ID();

-- 按钮 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片查询', @parentId, '1',  '#', '', 1, 0, 'F', '0', '0', 'news:news_img:query',        '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片新增', @parentId, '2',  '#', '', 1, 0, 'F', '0', '0', 'news:news_img:add',          '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片修改', @parentId, '3',  '#', '', 1, 0, 'F', '0', '0', 'news:news_img:edit',         '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片删除', @parentId, '4',  '#', '', 1, 0, 'F', '0', '0', 'news:news_img:remove',       '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻图片导出', @parentId, '5',  '#', '', 1, 0, 'F', '0', '0', 'news:news_img:export',       '#', 'admin', sysdate(), '', null, '');
