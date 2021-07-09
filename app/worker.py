#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name worker
__time__ = "2021/6/22 9:47"
from django.db import connection
from .tasks import run_oneforall_module,run_cdn_module,run_whois_info,run_crange,run_side_stations,run_ip_location,port_scanner,port_banner_scan,web_recongnize,sslinfo,screenshot,dirbuster_task,real_ip_recongnize
import json
from marmo.settings import CDN_MODULE,CRANGE_MODULE,SSLINFO_MODULE,SUBDOMAIN_MODULE,SCREENSHOT_MODULE,PORT_SCAN_MODULE,PORT_BANNER_MODULE,IP_LOCATION_MODULE,SIDE_STATIONS_MODULE,WHOIS_INFO_MODULE,WEB_ASSET_RECONGNIZE_MODULE,DIRBUSTER_MODULE,REAL_IP_RECONGNIZE_MODULE
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
from marmo.settings import DOMAIN_TASK_LIST,IP_TASK_LIST,SERVICE_TASK_LIST
from django_redis import get_redis_connection
from background_task import background
from celery.result import AsyncResult
from app.dao.module_function import ModuleFunctionDao
import re
'''
    域名定时器
    先从base_settings读取配置，获取域名资产该有的功能模块
    获取域名表上的资产信息，遍历每个域名资产
    每个域名资产最终的状态为XF,X是功能模块的序号line
    模块排序:根据line排序,
    
'''
@background
def domain_scheduler():
    cursor = connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        logger.log("domain scheduler")
        domain_asset_sql ="select domain.domain_name,domain.id,domain.project_id,project.name,domain.celery_status,domain.domain_type from online_asset_domain domain,marmo_project project where project.id=domain.project_id and project.status=1"
        logger.log("domain asset sql == "+str(domain_asset_sql))
        cursor.execute(domain_asset_sql)
        domain_asset_results = cursor.fetchall()
        logger.log("domain asset result =="+str(domain_asset_results))
        for domain_asset_result in domain_asset_results:
            domain = domain_asset_result[0]
            domain_id = domain_asset_result[1]
            project_id = domain_asset_result[2]
            project_name = domain_asset_result[3]
            celery_status = domain_asset_result[4]
            domain_type = domain_asset_result[5]
            domain_sql =""
            if domain_type =="1" or domain_type ==1:
                domain_sql = "select base_value from base_settings where base_type=2 and base_name='DOMAIN' and is_available=1 limit 1";
            elif domain_type =="2" or domain_type ==2:
                domain_sql = "select base_value from base_settings where base_type=2 and base_name='SUB_DOMAIN' and is_available=1 limit 1";
            cursor.execute(domain_sql)
            logger.log("domain scheduler sql ==" + str(domain_sql))
            domain_results = cursor.fetchall()
            if domain_results and len(domain_results) == 1:
                domain_value = domain_results[0][0]
                if domain_value:
                    domain_value = json.loads(domain_value)
                    line_sorted = sorted(domain_value, key=lambda x: x["line"])
                    '''
                        判断状态，然后判断模块名称
                    '''
                    for line in range(len(line_sorted)):
                        '''
                            line从1-4，先查询是否存在lineP,如果存在，资产放入队列，状态改成lineD,再查询是否存在line+1
                            line = line_sorted[x]
                            next_line = line_sorted[x+1]
                            asset,asset_type,asset_id,project_id,project_name
                        '''
                        current_lined = line_sorted[line]["line"]
                        name = line_sorted[line]["name"]
                        next_lined = 0
                        if line != len(line_sorted) - 1:
                            next_lined = int(line_sorted[line+1]["line"])
                        else:
                            '''
                                如果等于就不能通过下标获取，否则会引发list out of index
                            '''
                            next_lined = int(line_sorted[line]["line"]) + 1
                        logger.log("current linee =="+str(current_lined))
                        if celery_status ==str(current_lined)+"P":
                            '''
                                当前状态是XP,判断模块名称
                            '''
                            if name =="oneforall":
                                oneforall_task = run_oneforall_module.delay(domain, 1, int(domain_id), int(project_id),
                                                                            project_name)
                                task_id = oneforall_task.id
                                '''
                                    插入module_function表中
                                '''
                                insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                SUBDOMAIN_MODULE, 1, 1, int(domain_id), int(project_id), 1, task_id)
                                logger.log(insert_sql)
                                cursor.execute(insert_sql)
                                redis_connection.lpush(DOMAIN_TASK_LIST, task_id)
                                logger.log("oneforall模块推送task_list %s" % task_id)
                            elif name =="cdn":
                                    '''
                                        执行cdn模块
                                    '''
                                    cdn_task = run_cdn_module.delay(domain, 1, int(domain_id), int(project_id),
                                                                            project_name)
                                    cdn_task_id = cdn_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        CDN_MODULE, 1, 1, int(domain_id), int(project_id), 1, cdn_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(DOMAIN_TASK_LIST, cdn_task_id)
                                    logger.log("cdn模块推送task_list %s" % cdn_task_id)
                            elif name =="whois_info":
                                whois_info_task = run_whois_info.delay(domain, 1, int(domain_id), project_id, project_name)
                                whois_info_task_id = whois_info_task.id
                                insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                    WHOIS_INFO_MODULE, 1, 1, int(domain_id), int(project_id), 1, whois_info_task_id)
                                cursor.execute(insert_sql)
                                redis_connection.lpush(DOMAIN_TASK_LIST, whois_info_task_id)
                                logger.log("whois_info模块推送task_list %s" % whois_info_task_id)
                            elif name =="real_ip":
                                '''
                                    如果状态到了4P,那么证明域名已经完成了whois_info，要执行真实ip判断
                                '''
                                real_ip_task = real_ip_recongnize.delay(domain, 1, int(domain_id), project_id, project_name)
                                real_ip_task_id = real_ip_task.id
                                insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                    REAL_IP_RECONGNIZE_MODULE, 1, 1, int(domain_id), int(project_id), 1, real_ip_task_id)
                                cursor.execute(insert_sql)
                                redis_connection.lpush(DOMAIN_TASK_LIST, real_ip_task_id)
                                logger.log("real ip模块推送task_list %s" % real_ip_task_id)

                            '''
                                修改状态
                            '''
                            update_status_sql ="update online_asset_domain set celery_status='%s' where id=%d and domain_name='%s'"%(str(current_lined)+"D",int(domain_id),domain)
                            cursor.execute(update_status_sql)
                        elif celery_status ==str(current_lined)+"F":
                            '''
                                状态设置为下一个任务的lineP,然后
                            '''
                            update_status_sql = "update online_asset_domain set celery_status='%s' where id=%d and domain_name='%s'" % (
                            str(next_lined)+"P", int(domain_id), domain)
                            cursor.execute(update_status_sql)

    except Exception as e:
        logger.log("域名定时器出现异常=="+str(e.__str__()))


'''
    ip资产定时器
'''
@background
def ip_scheduler():
        cursor = connection.cursor()
        redis_connection = get_redis_connection("default")
        try:
            logger.log("ip scheduler")
            ip_asset_sql = "select ip.id,ip.ip,ip.project_id,project.name,ip.celery_status,ip.ip_type from online_asset_ip ip,marmo_project project where ip.project_id=project.id and project.`status`=1"
            logger.log("ip scheduler asset sql ==="+str(ip_asset_sql))
            cursor.execute(ip_asset_sql)
            ip_asset_results = cursor.fetchall()
            logger.log("ip scheduler asset results =="+str(ip_asset_results))
            for ip_asset_result in ip_asset_results:
                id = ip_asset_result[0]
                ip = ip_asset_result[1]
                project_id = ip_asset_result[2]
                project_name = ip_asset_result[3]
                celery_status = ip_asset_result[4]
                ip_type = ip_asset_result[5]
                ip_sql =""
                if ip_type =="1" or ip_type ==1:
                    ip_sql = "select base_value from base_settings where base_type=2 and base_name='IP' and is_available=1 limit 1";
                elif ip_type =="4" or ip_type ==4:
                    ip_sql ="select base_value from base_settings where base_type=2 and base_name='CIP' and is_available=1 limit 1";
                cursor.execute(ip_sql)
                ip_results = cursor.fetchall()
                if ip_results and len(ip_results) == 1:
                    ip_value = ip_results[0][0]
                    if ip_value:
                        ip_value = json.loads(ip_value)
                        line_sorted = sorted(ip_value, key=lambda x: x["line"])
                        '''
                            判断状态，然后判断模块名称
                        '''
                        for line in range(len(line_sorted)):
                            '''
                                line从5-8，先查询是否存在lineP,如果存在，资产放入队列，状态改成lineD,再查询是否存在line+1
                                line = line_sorted[x]
                                next_line = line_sorted[x+1]
                                asset,asset_type,asset_id,project_id,project_name
                            '''
                            current_lined = line_sorted[line]["line"]
                            name = line_sorted[line]["name"]
                            next_lined = 0
                            if line != len(line_sorted) - 1:
                                next_lined = int(line_sorted[line + 1]["line"])
                            else:
                                '''
                                    如果等于就不能通过下标获取，否则会引发list out of index
                                '''
                                next_lined = int(line_sorted[line]["line"]) + 1
                            logger.log("ip asset current lined =="+str(current_lined))
                            if celery_status == str(current_lined) + "P":
                                '''
                                    当前状态是XP,判断模块名称
                                '''
                                if name =="side_stations":
                                    '''
                                        旁站拓展
                                    '''
                                    run_side_stations_task = run_side_stations.delay(ip, 2, int(id),
                                                                                     project_id, project_name)
                                    side_stations_task_id = run_side_stations_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        SIDE_STATIONS_MODULE, 1, 2, int(id), int(project_id), 1,
                                        side_stations_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(IP_TASK_LIST, side_stations_task_id)
                                    logger.log("旁站模块推送task_list %s" % side_stations_task_id)
                                elif name =="crange":
                                    run_crange_task = run_crange.delay(ip, 2, int(id),project_id, project_name)
                                    crange_task_id = run_crange_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        CRANGE_MODULE, 1, 2, int(id), int(project_id), 1,
                                        crange_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(IP_TASK_LIST, crange_task_id)
                                    logger.log("C段拓展模块推送task_list %s" % crange_task_id)
                                elif name =="ip_location":
                                    run_ip_location_task = run_ip_location.delay(ip, 2, int(id),project_id, project_name)
                                    ip_location_task_id = run_ip_location_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        IP_LOCATION_MODULE, 1, 2, int(id), int(project_id), 1,
                                        ip_location_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(IP_TASK_LIST, ip_location_task_id)
                                    logger.log("IP地理位置模块推送task_list %s" % ip_location_task_id)
                                elif name =="portscan":
                                    port_type = int(ip_type)
                                    portscan_task = port_scanner.delay(ip, 2, int(id),project_id, project_name,port_type)
                                    portscan_task_id = portscan_task.id
                                    '''
                                        插入一条模块状态记录
                                    '''
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d ,%d ,%d,%d,%d,'%s',now(),now())" % (
                                        PORT_SCAN_MODULE,1, 2, int(id), int(project_id), 1, portscan_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(IP_TASK_LIST, portscan_task_id)
                                    logger.log("端口扫描模块推送task_list %s" % portscan_task_id)
                                '''
                                    更新状态
                                '''
                                update_sql ="update online_asset_ip set celery_status='%s' where id=%d and ip='%s'"%(str(current_lined)+"D",int(id),str(ip))
                                cursor.execute(update_sql)
                            elif celery_status == str(current_lined) + "F":
                                '''
                                    状态设置为下一个任务的lineP,然后
                                '''
                                update_sql ="update online_asset_ip set celery_status='%s' where id=%d and ip='%s'"%(str(next_lined)+"P",int(id),str(ip))
                                cursor.execute(update_sql)
        except Exception as e:
            logger.log("IP资产定时器出现异常==" + str(e.__str__()))
        finally:
            if cursor:
                cursor.close()



'''
    端口资产定时器
'''
@background
def service_scheduler():
    cursor = connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        logger.log("service scheduler")
        service_asset_sql = "select service.id,service.port,service.project_id,service.srv_type,project.name,service.celery_status,service.asset from online_asset_service service,marmo_project project where service.project_id=project.id and project.`status`=1 "
        cursor.execute(service_asset_sql)
        service_asset_results = cursor.fetchall()
        logger.log("service scheduler results ==="+str(service_asset_results))
        for service_asset_result in service_asset_results:
            id = service_asset_result[0]
            port = service_asset_result[1]
            project_id = service_asset_result[2]
            srv_type = service_asset_result[3]
            project_name = service_asset_result[4]
            celery_status=service_asset_result[5]
            asset = service_asset_result[6]
            domain =""
            if asset:
                '''
                    查询资产有没有相关联的域名
                '''
                domain_select_sql ="select domain.domain_name from online_asset_ip ip,domain_ip_relation dir,online_asset_domain domain where ip.id=dir.asset_domain_id and domain.id = dir.asset_domain_id and ip.ip='%s' limit 1"%(asset)
                cursor.execute(domain_select_sql)
                domain_select_results = cursor.fetchall()
                if domain_select_results and len(domain_select_results) >=1:
                    domain = domain_select_results[0][0]
            service_sql =""

            if srv_type ==1 or srv_type =="1" or srv_type =="2" or srv_type ==2:
                service_sql ="select base_value from base_settings where base_type=2 and base_name='SERVICE' and is_available=1 limit 1"
            else:
                '''
                    端口类型还没有确定,或者端口类型是其他端口
                '''
                service_sql = "select base_value from base_settings where base_type=2 and base_name='OTHERSERVICE' and is_available=1 limit 1"

            '''
                判断状态，然后判断模块名称
            '''
            cursor.execute(service_sql)
            service_results = cursor.fetchall()
            if service_results and len(service_results) == 1:
                service_value = service_results[0][0]
                if service_value:
                    service_value = json.loads(service_value)
                    line_sorted = sorted(service_value, key=lambda x: x["line"])
                    for line in range(len(line_sorted)):
                        '''
                            line从1-4，先查询是否存在lineP,如果存在，资产放入队列，状态改成lineD,再查询是否存在line+1
                            line = line_sorted[x]
                            next_line = line_sorted[x+1]
                            asset,asset_type,asset_id,project_id,project_name
                        '''
                        current_lined = line_sorted[line]["line"]
                        name = line_sorted[line]["name"]
                        next_lined = 0
                        if line != len(line_sorted) - 1:
                            next_lined = int(line_sorted[line + 1]["line"])
                        else:
                            '''
                                如果等于就不能通过下标获取，否则会引发list out of index
                            '''
                            next_lined = int(line_sorted[line]["line"]) + 1
                        logger.log("service current lined == "+str(current_lined)+"domain==="+str(domain))
                        do_srv_type = ""
                        if srv_type ==1 or srv_type =="1":
                            do_srv_type ="http"
                        elif srv_type ==2 or srv_type =="2":
                            do_srv_type ="https"
                        elif srv_type ==9 or srv_type =="9":
                            do_srv_type ="other"
                        if celery_status == str(current_lined) + "P":
                            '''
                                当前状态是XP,判断模块名称
                            '''
                            if name =="banner":
                                port_banner_task = port_banner_scan.delay(asset, 3, int(id), project_id,
                                                                          project_name, port)
                                port_banner_task_id = port_banner_task.id
                                insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                    PORT_BANNER_MODULE, 1, 3, int(id), int(project_id), 1, port_banner_task_id)
                                cursor.execute(insert_sql)
                                redis_connection.lpush(SERVICE_TASK_LIST, port_banner_task_id)
                                logger.log("端口banner探测模块推送task_list %s" % port_banner_task_id)

                            elif name =="web_recongnize":
                                '''
                                    web资产识别
                                '''
                                if do_srv_type =="https" or do_srv_type =="http":
                                    run_web_asset_task = web_recongnize.delay(asset, 3, int(id), int(project_id),
                                                                              project_name, port, domain, do_srv_type)
                                    run_web_asset_task_id = run_web_asset_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        WEB_ASSET_RECONGNIZE_MODULE, 1, 3, int(id), int(project_id), 1,
                                        run_web_asset_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(SERVICE_TASK_LIST, run_web_asset_task_id)
                                    logger.log("web资产识别模块推送task_list %s" % run_web_asset_task_id)

                            elif name =="sslinfo":
                                if do_srv_type == "https" or do_srv_type == "http":
                                    ssl_info_task = sslinfo.delay(asset, 3, int(id), int(project_id),
                                                                              project_name, port, domain, do_srv_type)
                                    ssl_info_task_id = ssl_info_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        SSLINFO_MODULE, 1, 3, int(id), int(project_id), 1, ssl_info_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(SERVICE_TASK_LIST, ssl_info_task_id)
                                    logger.log("SSL模块推送task_list %s" % ssl_info_task_id)

                            elif name =="screenshot":
                                if do_srv_type == "https" or do_srv_type == "http":
                                    screenshot_task = screenshot.delay(asset, 3, int(id), int(project_id),
                                                                              project_name, port, domain, do_srv_type)
                                    screenshot_task_id = screenshot_task.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        SCREENSHOT_MODULE, 1, 3, int(id), int(project_id), 1, screenshot_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(SERVICE_TASK_LIST, screenshot_task_id)
                                    logger.log("屏幕截图模块推送task_list %s" % screenshot_task_id)

                            elif name =="dirbuster":
                                if do_srv_type == "https" or do_srv_type == "http":
                                    dirbuster = dirbuster_task.delay(asset, 3, int(id), int(project_id),
                                                                              project_name, port, domain, do_srv_type)
                                    dirbuster_task_id = dirbuster.id
                                    insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                                        DIRBUSTER_MODULE, 1, 3, int(id), int(project_id), 1,
                                        dirbuster_task_id)
                                    cursor.execute(insert_sql)
                                    redis_connection.lpush(SERVICE_TASK_LIST, dirbuster_task_id)
                                    logger.log("目录爆破模块推送task_list %s" % dirbuster_task_id)

                            '''
                                修改状态为Doing
                            '''
                            update_service_sql = "update online_asset_service set celery_status='%s' where id=%d and port=%d" % (
                            str(current_lined) + "D", int(id), int(port))
                            cursor.execute(update_service_sql)

                        elif celery_status == str(current_lined) + "F":
                            '''
                                状态设置为下一个任务的lineP,然后
                            '''
                            update_service_sql ="update online_asset_service set celery_status='%s' where id=%d and port=%d"%(str(next_lined)+"P",int(id),int(port))
                            cursor.execute(update_service_sql)
    except Exception as e:
        logger.log("端口资产定时器出现异常==" + str(e.__str__()))
    finally:
        if cursor:
            cursor.close()


@background
def domain_worker_schduler():
        redis_connection = get_redis_connection("default")
        modulefunctiondao = ModuleFunctionDao()
        cursor = connection.cursor()
        try:
            last_len = redis_connection.llen(DOMAIN_TASK_LIST)
            logger.log("domain worker scheduler timing === " + str(last_len))
            if last_len > 0:
                task_id = redis_connection.rpop(DOMAIN_TASK_LIST)

                if task_id:
                    task_id = task_id.decode(encoding="UTF-8")
                    logger.log("task_id===" + str(task_id))
                    task_result = AsyncResult(id=task_id)
                    is_ready = task_result.ready()
                    state = task_result.state
                    logger.log("is_ready==" + str(is_ready))
                    logger.log(("state====" + str(state)))
                    if is_ready and state == "SUCCESS":
                        result = task_result.result
                        logger.log("result ==" + str(result))
                        if result:
                            if isinstance(result,str):
                                result = json.loads(result)
                            asset_id = ""
                            project_id = ""
                            module_name = ""
                            asset_type = ""
                            project_name =""
                            if result.__contains__("asset_id"):
                                asset_id = result["asset_id"]
                            if result.__contains__("project_id"):
                                project_id = result["project_id"]
                            if result.__contains__("asset_type"):
                                asset_type = result["asset_type"]
                            if result.__contains__("module_name"):
                                module_name = result["module_name"]
                            if result.__contains__("project_name"):
                                project_name =result["project_name"]
                            if asset_id and project_id and module_name and asset_type:
                                update_params = {
                                    "asset_id": asset_id,
                                    "project_id": project_id,
                                    "asset_type": asset_type,
                                    "module_name": module_name
                                }
                                if project_name:
                                    update_params["project_name"]=project_name
                                if result.__contains__("exists_data"):
                                    exists_data = result["exists_data"]
                                    if exists_data:  # 存在数据
                                        update_params["module_log"] = result["data"]
                                    else:
                                        update_params["module_log"] = ""
                                if result.__contains__("status_code"):
                                    status_code = result["status_code"]
                                    if status_code == 3:
                                        update_params["fail_reason"] = result["fail_reason"]
                                    update_params["module_status"] = status_code
                                logger.log(" domain update params =="+str(update_params))
                                modulefunctiondao.update_module_function(update_params)
                            if asset_id:
                                '''
                                    更新资产的状态,先查询出资产的信息
                                '''
                                select_sql ="select celery_status from online_asset_domain where id=%d"%(int(asset_id))
                                logger.log("domain update sql =="+str(select_sql))
                                cursor.execute(select_sql)
                                celery_results = cursor.fetchall()
                                logger.log("domain update results =="+str(celery_results))
                                if celery_results and len(celery_results) >=1:
                                    celery_status = celery_results[0][0]
                                    logger.log("domain celery status =="+str(celery_status))
                                    if celery_status:
                                        current_line_res = re.findall("\d+",celery_status,re.S)
                                        logger.log("domain celery res =="+str(current_line_res))
                                        if current_line_res and len(current_line_res) ==1:
                                            update_sql ="update online_asset_domain set celery_status='%s' where id=%d"%(str(current_line_res[0])+"F",int(asset_id))
                                            logger.log("update domain sql =="+str(update_sql))
                                            cursor.execute(update_sql)
                    else:
                        redis_connection.lpush(DOMAIN_TASK_LIST, task_id)
        except Exception as e:
            logger.log("domain worker 获取任务结果出现异常==" + str(e.__str__()))
        finally:
            if cursor:
                cursor.close()


@background
def ip_worker_schduler():
        redis_connection = get_redis_connection("default")
        modulefunctiondao = ModuleFunctionDao()
        cursor = connection.cursor()
        try:
            last_len = redis_connection.llen(IP_TASK_LIST)
            logger.log("ip worker scheduler timing === " + str(last_len))
            if last_len > 0:
                task_id = redis_connection.rpop(IP_TASK_LIST)

                if task_id:
                    task_id = task_id.decode(encoding="UTF-8")
                    logger.log("task_id===" + str(task_id))
                    task_result = AsyncResult(id=task_id)
                    is_ready = task_result.ready()
                    state = task_result.state
                    logger.log("is_ready==" + str(is_ready))
                    logger.log(("state====" + str(state)))
                    if is_ready and state == "SUCCESS":
                        result = task_result.result
                        logger.log("result ==" + str(result))
                        if result:
                            if isinstance(result,str):
                                result = json.loads(result)
                            asset_id = ""
                            project_id = ""
                            module_name = ""
                            asset_type = ""
                            project_name =""
                            if result.__contains__("asset_id"):
                                asset_id = result["asset_id"]
                            if result.__contains__("project_id"):
                                project_id = result["project_id"]
                            if result.__contains__("asset_type"):
                                asset_type = result["asset_type"]
                            if result.__contains__("module_name"):
                                module_name = result["module_name"]
                            if result.__contains__("project_name"):
                                project_name = result["project_name"]
                            if asset_id and project_id and module_name and asset_type:
                                update_params = {
                                    "asset_id": asset_id,
                                    "project_id": project_id,
                                    "asset_type": asset_type,
                                    "module_name": module_name,

                                }
                                if project_name:
                                    update_params["project_name"]=project_name
                                if result.__contains__("exists_data"):
                                    exists_data = result["exists_data"]
                                    if exists_data:  # 存在数据
                                        update_params["module_log"] = result["data"]
                                    else:
                                        update_params["module_log"] = ""
                                if result.__contains__("status_code"):
                                    status_code = result["status_code"]
                                    if status_code == 3:
                                        update_params["fail_reason"] = result["fail_reason"]
                                    update_params["module_status"] = status_code
                                logger.log(" ip update params ==" + str(update_params))
                                modulefunctiondao.update_module_function(update_params)
                            if asset_id:
                                '''
                                    更新资产的状态,先查询出资产的信息
                                '''
                                select_sql ="select celery_status from online_asset_ip where id=%d"%(int(asset_id))
                                logger.log("ip update sql =="+str(select_sql))
                                cursor.execute(select_sql)
                                celery_results = cursor.fetchall()
                                logger.log("ip update results =="+str(celery_results))
                                if celery_results and len(celery_results) >=1:
                                    celery_status = celery_results[0][0]
                                    logger.log("ip celery status =="+str(celery_status))
                                    if celery_status:
                                        current_line_res = re.findall("\d+",celery_status,re.S)
                                        logger.log("ip celery res =="+str(current_line_res))
                                        if current_line_res and len(current_line_res) ==1:
                                            update_sql ="update online_asset_ip set celery_status='%s' where id=%d"%(str(current_line_res[0])+"F",int(asset_id))
                                            cursor.execute(update_sql)

                    else:
                        redis_connection.lpush(IP_TASK_LIST, task_id)
        except Exception as e:
            logger.log("ip worker 获取任务结果出现异常==" + str(e.__str__()))
        finally:
            if cursor:
                cursor.close


@background
def service_worker_schduler():
        redis_connection = get_redis_connection("default")
        modulefunctiondao = ModuleFunctionDao()
        cursor = connection.cursor()
        try:
            last_len = redis_connection.llen(SERVICE_TASK_LIST)
            logger.log("service worker scheduler timing === " + str(last_len))
            if last_len > 0:
                task_id = redis_connection.rpop(SERVICE_TASK_LIST)

                if task_id:
                    task_id = task_id.decode(encoding="UTF-8")
                    logger.log("ip worker task_id===" + str(task_id))
                    task_result = AsyncResult(id=task_id)
                    is_ready = task_result.ready()
                    state = task_result.state
                    logger.log("ip worker is_ready==" + str(is_ready))
                    logger.log(("ip worker state====" + str(state)))
                    if is_ready and state == "SUCCESS":
                        result = task_result.result
                        logger.log("result ==" + str(result))
                        if result:
                            if isinstance(result, str):
                                result = json.loads(result)
                            asset_id = ""
                            project_id = ""
                            module_name = ""
                            asset_type = ""
                            project_name =""
                            if result.__contains__("asset_id"):
                                asset_id = result["asset_id"]
                            if result.__contains__("project_id"):
                                project_id = result["project_id"]
                            if result.__contains__("asset_type"):
                                asset_type = result["asset_type"]
                            if result.__contains__("module_name"):
                                module_name = result["module_name"]
                            if result.__contains__("project_name"):
                                project_name = result["project_name"]
                            if asset_id and project_id and module_name and asset_type:
                                update_params = {
                                    "asset_id": asset_id,
                                    "project_id": project_id,
                                    "asset_type": asset_type,
                                    "module_name": module_name
                                }
                                if project_name:
                                    update_params["project_name"]=project_name
                                if result.__contains__("exists_data"):
                                    exists_data = result["exists_data"]
                                    if exists_data:  # 存在数据
                                        update_params["module_log"] = result["data"]
                                    else:
                                        update_params["module_log"] = ""
                                if result.__contains__("status_code"):
                                    status_code = result["status_code"]
                                    if status_code == 3:
                                        update_params["fail_reason"] = result["fail_reason"]
                                    update_params["module_status"] = status_code
                                logger.log(" service update params ==" + str(update_params))
                                modulefunctiondao.update_module_function(update_params)

                            if asset_id:
                                '''
                                    更新资产的状态,先查询出资产的信息
                                '''
                                select_sql ="select celery_status from online_asset_service where id=%d"%(int(asset_id))
                                logger.log("service update sql =="+str(select_sql))
                                cursor.execute(select_sql)
                                celery_results = cursor.fetchall()
                                logger.log("service update results =="+str(celery_results))
                                if celery_results and len(celery_results) >=1:
                                    celery_status = celery_results[0][0]
                                    logger.log("celery status =="+str(celery_status))
                                    if celery_status:
                                        current_line_res = re.findall("\d+",celery_status,re.S)
                                        logger.log("celery res =="+str(current_line_res))
                                        if current_line_res and len(current_line_res) ==1:
                                            update_sql ="update online_asset_service set celery_status='%s' where id=%d"%(str(current_line_res[0])+"F",int(asset_id))
                                            cursor.execute(update_sql)



                    else:
                        redis_connection.lpush(SERVICE_TASK_LIST, task_id)
        except Exception as e:
            logger.log("service worker 获取任务结果出现异常==" + str(e.__str__()))
        finally:
            if cursor:
                cursor.close()



















