drop table if exists marmo_project;
create table marmo_project(
	id int not null auto_increment,
	customer varchar(64) not null comment '所属客户',
	name varchar(64) not null comment '项目名称',
	comments MEDIUMTEXT comment '备注',
	`status` int not null default 0 comment '状态(0-未开始,1-进行中,2-结束)',
	delivery_date date comment '沟通交付日期',
	actual_delivery_date date comment '实际交付日期',
	assets_scope text not null comment '资产范围',
	work_time varchar(128) not null  comment '渗透时间要求',
	pentest_level varchar(64) not null comment '渗透深度',
	pentest_tech text  comment '渗透手段限制',
	attachment_id int comment '报告模板下载地址',
	summary LONGTEXT comment '总结汇报',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '修改时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '项目表';

drop table if exists project_charge_person;
create table project_charge_person(
	id int not null auto_increment,
	group_id int not null comment '组id',
	user_id int not null comment '负责人',
	project_id int not null comment '项目',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '修改时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '项目负责人表';

drop table if exists daily_report;
create table daily_report(
 id int not null auto_increment,
 report_date date not null comment '日报日期',
 content text not null  comment '日报内容',
 project_id int not null comment '关联的项目表',
 create_time datetime not null comment '提交时间',
 update_time datetime not null comment '修改时间',
 primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '日报数据表';

drop table if exists attachment;
create table  attachment(
	id int not null auto_increment,
	download_url varchar(256) not null comment '下载地址',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key (id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '附件表';


drop table if exists project_attachment_relation;
create table  project_attachment_relation(
	id int not null auto_increment,
	type int not null comment '附件类型(1-日报附件,2-资产附件,3-项目报告模板)',
	user_id varchar(32) not null comment '提交人',
	attachment_id varchar(32) not null comment '附件ID',
	project_id int not null comment '关联的项目表',
	external_id int not null comment '外表ID',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '附件关系表';

drop table if exists offline_asset;
create table offline_asset(
 id int not null auto_increment,
 asset_type int not null comment '资产类型(1-app,2-windows,3-linux)',
 platform int not null comment '所属平台(1-android,2-apple,3-windows,4-linux,5-其他)',
 version varchar(32) comment 'app版本',
 is_reinforce int comment '是否加固(0-没有加固,1-已经加固)',
 reinforce_vendor varchar(64) comment '加固信息',
 project_id int not null comment '项目id',
 description text not null comment '备注',
 app_file_id int comment 'app下载地址id',
 attachment_id int comment '附件id',
 create_time datetime not null comment '创建时间',
update_time datetime not null comment '创建时间',
 primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '离线资产表';


drop table if exists online_security;
create table online_security(
	id int not null auto_increment,
	security_name varchar(64) not null comment '设备名称',
	company varchar(64) not null comment '所属公司',
	vuln MEDIUMTEXT comment '安全设备漏洞',
	project_id int not null comment '关联的项目',
	source int not null default 1 comment '来源,1-程序添加,2-人工添加',
	source_detail text comment '来源详情',
	description text not null comment '备注',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '安全设备表';

drop table if exists online_asset_domain;
create table online_asset_domain(
	id int not null auto_increment,
	domain_type int not null comment '资产类型(1-二级域名,2-三级/四级/五级域名)',
	domain_name varchar(256) not null comment '域名值',
	whois_info  text comment '非结构化whois数据存储',
	extra_info text comment '域名情报',
	source int not null default 1 comment '来源,1-程序添加,2-人工添加',
	source_detail text comment '来源详情',
	project_id int not null comment '关联的项目',
	is_include_cdn_ip int not null comment '是否包含cdn的IP,1-是,2-否',
	description text not null comment '备注',
	dirbuster longtext comment '目录爆破结果',
	celery_status int not null default 1 comment '1-未执行过,2-队列中,3-已完成,4-有异常',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)

)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '在线域名资产表';

drop table if exists online_asset_ip;
create table online_asset_ip(
	id int not null auto_increment,
	ip_type int not null comment 'ip类型(1-真实IP,2-CDN,3-未知,4-C段IP)',
	extra_info text comment 'ip情报',
	rdns_history text comment '反向解析历史',
	location text not null comment 'ip地理位置',
	ip varchar(128) not null comment 'ip值',
	org text not null comment '组织出口',
	source int not null default 1 comment '来源,1-程序添加,2-人工添加',
	source_detail text comment '来源详情',
	description text not null comment '备注',
	is_belongs_to int not null comment 'ip是否属于目标方 1-是,2-否',
	project_id int not null comment '关联的项目',
	dirbuster longtext comment '目录爆破结果',
	celery_status int not null default 1 comment '1-未执行过,2-队列中,3-已完成,4-有异常,5-待端口探测',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '在线IP资产表';

drop table if exists domain_ip_relation;
create table domain_ip_relation(
	id int not null auto_increment,
	asset_domain_id int not null comment '域名id',
	asset_ip_id int not null comment 'ip资产id',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key (id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '域名和IP关联表';


drop table if exists ip_service_relation;
create table ip_service_relation(
	id int not null auto_increment,
	asset_ip_id int not null comment 'ip资产id',
	asset_service_id int not null comment '服务ID',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key (id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '域名和IP关联表';

drop table if exists online_asset_service;
create table online_asset_service(
	id int not null auto_increment,
	`port` varchar(32) comment '端口',
	srv_type int comment '基本类型 0-未知,1-http,2-https,9-other',
	is_deep_http_recongnize int comment '是否经过深度分析 1-是,2-否',
	project_id int not null comment '关联的项目',
	service_name varchar(256) comment 'banner名称',
	service_version varchar(32) comment 'banner版本',
	web_asset_id int comment 'web资产表id',
	source int not null comment '来源 1-人工添加，2-程序添加',
	source_detail text comment '来源详情',
	description text comment '备注',
	asset varchar(256) not null comment '关联资产',
	asset_type int comment '管理资产,1-domain,2-ip',
	celery_status int not null default 1 comment '1-未执行过,2-队列中,3-已完成,4-有异常,5-待端口运行',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key (id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '端口表';

drop table if exists service_component_tag_relation;
create table service_component_tag_relation(
	id int not null auto_increment,
	component_id int not null comment '组件标签id',
	service_id int not null comment '服务id',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key (id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '服务标签关系表';

drop table if exists component_tag;
create table component_tag(
	id int not null auto_increment,
	component_name varchar(64)  comment '组件名称',
	version varchar(32) comment '组件版本',
	component_type int not null default 0 comment '组件类型(0-未知,1-开发语言,2-中间件,3-模块/框架,4-CMS)',
	create_source varchar(64) not null comment '创建来源(manual-手工创建,from-从项目中创建)',
	source_detail text comment '来源详情',
	project_id int not null comment '关联项目',
	description text comment '备注',
	asset varchar(256) comment '关联资产',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '组件标签库';

drop table if exists process_info;
create table process_info(
	id int not null auto_increment,
	info_type int not null comment '信息类型(1-渗透信息)',
	info_status int not null comment '信息状态(1-信息,2-待解决,3-已解决)',
	info_level int not null comment '信息重要性(1-低,2-中,3-高)',
	info_content text not null comment '内容',
	user_id int not null comment '给渗透信息添加负责人',
	asset varchar(256) not null comment '关联资产',
	responser int not null comment '负责人',
	project_id int not null comment '绑定的项目',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '过程信息';

drop table if exists vuln_info;
create table vuln_info(
	id int not null auto_increment,
	vuln_name text not null comment '漏洞名称',
	vuln_level int not null comment '漏洞评级(1-高,2-中,3-低)',
	vuln_desc text not null comment '漏洞描述',
	vuln_details text not null comment '漏洞详情&复现过程',
	vuln_affect text not null comment '漏洞影响',
	vuln_status int not null comment '漏洞状态(1-确认漏洞,2-误报,3-已修复,4-待确认)',
	is_retest int not null default 0 comment '是否复测过(1-是,2-否)',
	user_id int not null comment '漏洞创建人',
	project_id int not null comment '绑定的项目',
	asset_type int not null comment '1-domain,2-ip,3-安全设备',
	asset varchar(256) not null comment '关联资产',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '漏洞信息';

drop table if exists marmo_url;
create table marmo_url(
	id int not null auto_increment,
	url varchar(128) not null,
	project_id int not null comment '项目',
	method varchar(10) not null comment '方法',
	`host` varchar(10) not null comment 'host',
	procotol varchar(10) not null comment '协议',
	`port` int not null comment '端口',
	raw_req text comment '原始请求',
	modify_req text not null comment '修改后的请求',
	response text not null comment '响应',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci comment '渗透平台url集';

-- 用户和组的关系
drop table if exists `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `account` varchar(256) NOT NULL comment '账号',
  `password` varchar(256) NOT NULL comment '密码',
  `realname` varchar(256) comment '真实姓名',
  `nickname` varchar(256) comment '昵称',
  `avatar` varchar(256) comment '头像',
  `birthday` date comment '生日',
  `gender` int NOT NULL default 1 comment '性别 1-男,2-女',
  `email` varchar(256) comment '邮箱',
  `qq` varchar(20) comment 'qq号',
  `mobile` int(11) comment '手机号',
  `weixin` varchar(256) comment '微信号',
  `dingding` varchar(256) comment '钉钉',
  `whatsapp` varchar(256) comment 'whatsapp',
  `address` varchar(256) comment '地址',
   create_time datetime not null comment '创建时间',
   update_time datetime not null comment '创建时间',
  PRIMARY KEY  (`id`)
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '用户表';

drop table if exists authority;
create table authority(
	id int not null auto_increment,
	can_read int not null default 0 comment '是否可读(0-否,1-是)',
	can_write int not null default 0 comment '是否可写(0-否,1-是)',
	can_delete int not null default 0 comment '是否可删除(0-否,1-是)',
	can_add int not null default 0 comment '是否可添加(0-否,1-是)',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)

)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '权限表';

drop table if exists `group`;
create table `group`(
	id int not null auto_increment,
	group_name varchar(64) not null comment '组名',
	description text comment '描述',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '用户组';

drop table if exists group_authority_relation;
create table group_authority_relation(
	id int not null auto_increment,
	group_id int not null comment '组id',
	authority_id int not null comment '权限id',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '组和权限的关系表';

drop table if exists asset_relation;
create table asset_relation(
	id int not null auto_increment,
	external_id int not null comment '离线资产id',
	user_id int not null comment '负责人',
	project_id int not null comment '项目id',
	`type` int not null comment '类型(1-域名,2-安全设备,3-IP,4-漏洞,5-渗透信息,6-服务)',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)

)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '关系表';

drop table if exists marmo_log;
create table marmo_log(
	id int not null auto_increment,
	`module` varchar(128) not null comment '模块名称',
	`type` char(1) not null comment '1-ip,2-domain,3-service,4-port,5-cdn',
	`module_log` longtext not null comment '日志',
	asset_id int not null comment '管理资源ID'
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '日志表';

drop table if exists flow_log;
create table flow_log(
	id int not null auto_increment,
	`module_id` int not null comment '模块id',
	`log` text not null comment '日志',
	user_id int not null comment '负责人',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '审计日志表';

drop table if exists process_info_relation;
create table process_info_relation(
	id int not null auto_increment,
	receiver int not null comment '被指派人',
	process_info_id int not null comment '渗透信息表id',
	sender int not null comment '指派人',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '渗透信息关系表';

/*
drop table if exists asset_module_relation;
create table  asset_module_relation(
	id int not null auto_increment,
	asset_id int not null comment '资产id',
	module_id int not null comment '模块id',
	taskid varchar(128) not null comment '任务id',
	task_result varchar(128) comment '任务结果',
	task_status varchar(128) comment '任务状态',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '资产模块关系表';*/

drop table if exists base_settings;
create table base_settings(
	id int not null auto_increment,
	base_type varchar(128) not null comment '类型',
	base_name varchar(128) not null comment '类型名称',
	base_value varchar(512) not null comment '基本值',
	is_available  int(1) not null default 1 comment '是否有效,1-有效,2-失效',
	parent_id int comment '父类ID',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '配置表';

drop table if exists web_asset;
create table web_asset(
	id int not null auto_increment,
	url varchar(256) not null comment '链接',
	status_code int not null comment '状态码',
	source int  comment '来源',
	source_detail text comment '来源详情',
	screenshot varchar(256) not null comment '网页截图地址',
	asset_id int not null comment '端口id',
	http_ssl_version varchar(32) comment 'ssl版本',
	http_title varchar(1024) comment '网页标题',
	http_resp_body text comment '响应体',
	http_resp_header text comment '响应头',
	project_id int not null comment '关联的项目',
	asset varchar(256) not null comment '关联资产',
	asset_type int not null comment '资产类型 1-ip,2-domain',
	url_type int not null comment '类型 1-首页,2-爆破',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT 'web资产表';

drop table if exists ssl_certificates;
create table ssl_certificates(
	id int not null auto_increment,
	info text not null comment '证书信息',
	port int not null comment '端口',
	asset varchar(256) not null comment '资产',
	`type` int not null comment '类型 1-域名，2-ip',
	hash varchar(256)  comment '证书hash值',
	project_id int not null comment '关联项目',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT 'ssl证书表';

drop table if exists module_function;
create table module_function(
	id int not null auto_increment,
	module_name varchar(256) not null comment '模块功能',
	module_status int not null comment '模块状态,0-未开始,1-进行中,2-已结束,3-有异常',
	module_log longtext comment '模块日志',
	asset_type int not null comment '资产类型,1-domain,2-ip,3-service,4-组件',
	asset_id int not null comment '资产id',
	fail_reason text comment '失败原因',
	project_id int not null comment '关联项目',
	task_id varchar(256) comment '任务id',
	task_status int not null comment '任务状态 1-进行中,2-已结束',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '模块功能表';

drop table if exists side_stations;
create table side_stations(
	id int not null auto_increment,
	info text not null comment '旁站信息',
	asset_id int not null comment 'ip资产id',
	project_id int not null comment '关联项目',
	create_time datetime not null comment '创建时间',
	update_time datetime not null comment '创建时间',
	primary key(id)
)ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT '旁站表';


-- 插入数据
insert into base_settings(base_type,base_name,base_value,is_available,create_time,update_time) values('1','个人中心','http://127.0.0.1:8080/user?type=html',1,now(),now()),
('1','项目管理','http://127.0.0.1:8080/project?type=html',1,now(),now())
,('1','资产管理','http://127.0.0.1:8080/user?type=html',1,now(),now());

insert into `group`(group_name,description,create_time,update_time) values('专家组','专家组',now(),now()),
('信息组','信息组',now(),now()),
('工具组','工具组',now(),now());

insert into user(account,password,nickname,create_time,update_time) values("liangguanjie",md5("liangguanjie!qaz@WSX"),"梁冠杰",now(),now()),
("zouyuepeng",md5("zouyuepeng!qaz@WSX"),"邹跃鹏",now(),now()),
("zhongshiguo",md5("zhongshiguo!qaz@WSX"),"钟仕国",now(),now()),
("wangxiaotian",md5("wangxiaotian!qaz@WSX"),"王笑天",now(),now()),
("yuhongjie",md5("yuhongjie!qaz@WSX"),"余鸿杰",now(),now());

-- 创建渗透任务和任务流转历史
insert into process_info (info_type,info_status,info_level,info_content,asset,user_id,project_id,responser,create_time,update_time) values(1,1,2,"测试百度的上传漏洞","www.baidu.com",1,1,2,now(),now());

insert into process_info_relation(receiver,sender,process_info_id,create_time,update_time) values(2,1,1,now(),now()),(3,2,1,now(),now()),(1,3,1,now(),now());
INSERT INTO base_settings ( base_type, base_name, base_value, create_time, update_time )
VALUES
	(
		2,
		"DOMAIN",'[{ "name" : "oneforall",
		"line" : 1,
		"title" : "子域名收集&爆破" },{ "name" : "cdn",
		"line" : 3,
		"title" : "cdn判断" },{ "name" : "whois_info",
		"line" : 2,
		"title" : "whois_info信息收集" },{ "name" : "real_ip",
		"line" : 4,
		"title" : "真实IP判断" }]',
		now(),
	now()),
	(
		2,
		"SUB_DOMAIN",'[{ "name" : "cdn",
		"line" : 3,
		"title" : "cdn判断" },{ "name" : "real_ip",
		"line" : 4,
		"title" : "真实IP判断" }]',
		now(),
	now()),
	(
		2,
		"IP",'[{ "name" : "side_stations",
		"line" : 5,
		"title" : "旁站拓展" },{ "name" : "crange",
		"line" : 6,
		"title" : "C段拓展" },{ "name" : "ip_location",
		"line" : 7,
		"title" : "IP位置&出口诊断" },{ "name" : "portscan",
		"line" : 8,
		"title" : "端口探测" }]',
		now(),
	now()),
	(
		2,
		"CIP",'[{ "name" : "ip_location",
		"line" : 7,
		"title" : "IP位置&出口诊断" },{ "name" : "portscan",
		"line" : 8,
		"title" : "端口探测" }]',
		now(),
	now()),
	(
		2,
		"SERVICE",'[{ "name" : "banner",
		"line" : 9,
		"title" : "端口banner探测" },{ "name" : "web_recongnize",
		"line" : 10,
		"title" : "web资产深度识别" },{ "name" : "sslinfo",
		"line" : 11,
		"title" : "ssl证书获取" },{ "name" : "screenshot",
		"line" : 12,
		"title" : "网站截图" },{ "name" : "dirbuster",
		"line" : 13,
		"title" : "目录爆破" }]',
	now(),
	now()),
	(
		2,
		"OTHERSERVICE",'[{ "name" : "banner",
		"line" : 9,
		"title" : "端口banner探测" }]',
	now(),
	now());

insert into base_settings(base_type,base_name,base_value,create_time,update_time) values(3,"子域名收集&爆破",1,now(),now()),(3,"whois_info信息收集",2,now(),now())
,(3,"cdn判断",3,now(),now()),(3,"真实IP判断",4,now(),now()),(3,"旁站拓展",5,now(),now()),(3,"c段扫描",6,now(),now()),(3,"IP位置&出口诊断",7,now(),now())
,(3,"端口探测",8,now(),now()),(3,"端口banner探测",9,now(),now())
,(3,"web资产深度识别",10,now(),now()),(3,"ssl证书获取",11,now(),now()),(3,"网站截图",12,now(),now()),(3,"目录爆破",13,now(),now());

insert into base_settings(base_type,base_name,base_value,create_time,update_time) values(4,"domain_start",1,now(),now()),(4,"domain_end",4,now(),now())
(4,"sub_domain_start",3,now(),now()),(4,"sub_domain_end",4,now(),now()),(4,"real_ip_start",5,now(),now()),(4,"crange_ip_start",7,now(),now()),(4,"real_ip_end",8,now(),now())
,(4,"crange_ip_end",8,now(),now()),(4,"webservice_start",9,now(),now()),(4,"webservice_end",13,now(),now()),(4,"otherservice_start",9,now(),now()),(4,"otherservice_end",9,now(),now())

