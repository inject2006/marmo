alter table process_info_relation drop column asset_id;
alter table process_info_relation drop column `type`;
alter table process_info add asset varchar(256) not null comment '关联资产';
alter table process_info add responser int not null comment '负责人';

-- 创建渗透任务和任务流转历史
insert into process_info (info_type,info_status,info_level,info_content,asset,user_id,create_time,update_time) values(1,1,2,"测试百度的上传漏洞","www.baidu.com",1,now(),now());

insert into process_info_relation(receiver,sender,process_info_id,create_time,update_time) values(2,1,1,now(),now()),(3,2,1,now(),now()),(1,3,1,now(),now());