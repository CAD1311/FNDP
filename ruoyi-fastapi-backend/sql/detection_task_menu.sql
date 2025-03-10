-- 菜单 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('新闻检测', '3', '1', 'detection_task', 'detection/detection_task/index', 1, 0, 'C', '0', '0', 'detection:detection_task:list', '#', 'admin', sysdate(), '', null, '新闻检测菜单');

-- 按钮父菜单ID
SELECT @parentId := LAST_INSERT_ID();

-- 按钮 SQL
insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('检测任务查询', @parentId, '1',  '#', '', 1, 0, 'F', '0', '0', 'detection:detection_task:query',        '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('检测任务新增', @parentId, '2',  '#', '', 1, 0, 'F', '0', '0', 'detection:detection_task:add',          '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('检测任务删除', @parentId, '3',  '#', '', 1, 0, 'F', '0', '0', 'detection:detection_task:remove',       '#', 'admin', sysdate(), '', null, '');

insert into sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
values('检测任务导出', @parentId, '4',  '#', '', 1, 0, 'F', '0', '0', 'detection:detection_task:export',       '#', 'admin', sysdate(), '', null, '');
