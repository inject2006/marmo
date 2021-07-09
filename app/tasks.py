from __future__ import absolute_import, unicode_literals
#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name tasks
__time__ = "2021/6/8 10:11"

from celery import shared_task
from app.module import *
from marmo.settings import CDN_MODULE,CRANGE_MODULE,SSLINFO_MODULE,SUBDOMAIN_MODULE,SCREENSHOT_MODULE,PORT_SCAN_MODULE,PORT_BANNER_MODULE,IP_LOCATION_MODULE,SIDE_STATIONS_MODULE,WHOIS_INFO_MODULE,WEB_ASSET_RECONGNIZE_MODULE,DIRBUSTER_MODULE,REAL_IP_RECONGNIZE_MODULE
from django.db import connection
from django_redis import get_redis_connection
from datetime import datetime as ddt
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
from marmo.settings import DOMAIN_TASK_LIST,IP_TASK_LIST,SERVICE_TASK_LIST
'''
    子域名收集&爆破任务
    input:
    {
        asset
        asset_type
        asset_id
        project_id
        project_name
        module_name
        
    }
'''
@shared_task
def run_oneforall_module(asset,asset_type,asset_id,project_id,project_name):

    oneforall = OneForAll({"domain_name":asset,"module_name":SUBDOMAIN_MODULE,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name})
    return oneforall.run()

'''
    运行cdn判断模块
    input:
    {
        project_id
        module_name
        domain
    }
'''
@shared_task
def run_cdn_module(asset,asset_type,asset_id,project_id,project_name):
    logger.log("run cdn module")
    cdn = Cdn({"project_id":project_id,"domain":asset,"module_name":CDN_MODULE,"project_name":project_name,"asset_id":asset_id,"asset_type":asset_type})
    return cdn.run()

@shared_task
def run_whois_info(asset,asset_type,asset_id,project_id,project_name):
    whois_info = WhoisInfo({"domain":asset,"module_name":WHOIS_INFO_MODULE,"project_name":project_name,"project_id":project_id,"asset_id":asset_id,"asset_type":asset_type})
    return whois_info.run()


'''
    web资产识别模块
'''
@shared_task
def web_recongnize(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type):
    webasset =WebAsset({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name,"module_name":WEB_ASSET_RECONGNIZE_MODULE,"port":port,"domain":domain,"srv_type":srv_type})
    return webasset.run()

'''
    真实IP判断模块
'''
@shared_task
def run_real_ip_recongnize(asset,asset_type,asset_id,project_id,project_name):
    real_ip = RealIpRecongnize({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name})
    return real_ip.run()

'''
    web网页截图模块
'''
@shared_task
def screenshot(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type):
    screenshot =ScreenShot({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name,"module_name":SCREENSHOT_MODULE,"port":port,"domain":domain,"srv_type":srv_type})
    return screenshot.run()

'''
    ssl信息获取模块
'''
@shared_task
def sslinfo(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type):
    ssl = SslInfo({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name,"module_name":SSLINFO_MODULE,"port":port,"domain":domain,"srv_type":srv_type})
    return ssl.run() #返回文件位置
    # sslPrint =SslFingerPrint({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name,"module_name":SSLINFO_MODULE,"port":port,"domain":domain,"srv_type":srv_type})
    # sslPrint.run()


@shared_task
def run_side_stations(asset,asset_type,asset_id,project_id,project_name):
    side_station=SideStations({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"module_name":SIDE_STATIONS_MODULE,"project_name":project_name})
    return side_station.run()

@shared_task
def run_crange(asset,asset_type,asset_id,project_id,project_name):
    crange = CDuan({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"module_name":CRANGE_MODULE,"project_name":project_name})
    return crange.run()

@shared_task
def run_ip_location(asset,asset_type,asset_id,project_id,project_name):
    ip_location = IPLocation({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"module_name":IP_LOCATION_MODULE,"project_name":project_name})
    return ip_location.run()


@shared_task
def port_scanner(asset,asset_type,asset_id,project_id,project_name,port_type):
    '''
        端口探测
    :return:
    '''
    port_scan = PortScan({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"module_name":PORT_SCAN_MODULE,"project_name":project_name,"type":port_type})
    return port_scan.run()

'''
    banner探测模块
    input:{
        asset
        port
        module_name
        project_id
        project_name
        asset_type
        asset_id
        asset
    }
'''
@shared_task
def port_banner_scan(asset,asset_type,asset_id,project_id,project_name,port):
    portbanner = PortBanner({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"module_name":PORT_BANNER_MODULE,"project_name":project_name,"port":port})
    return portbanner.run()


'''
    目录爆破
'''
@shared_task
def dirbuster_task(asset,asset_type,service_id,project_id,project_name,port,domain,srv_type):
     dirbuster = DirBuster({"asset":asset,"asset_type":asset_type,"asset_id":service_id,"project_id":project_id,"project_name":project_name,"port":port,"domain":domain,"srv_type":srv_type,"module_name":DIRBUSTER_MODULE})
     return dirbuster.run()

'''
    真实ip判断
'''
@shared_task
def real_ip_recongnize(asset,asset_type,asset_id,project_id,project_name):
    real_ip = RealIpRecongnize({"asset":asset,"asset_type":asset_type,"asset_id":asset_id,"project_id":project_id,"project_name":project_name,"module_name":REAL_IP_RECONGNIZE_MODULE})
    return real_ip.run()






'''
    主域名运行按钮逻辑,触发逻辑是后台的主域名运行按钮
    模块:
    子域名收集模块
    cdn判断模块
    whois_info模块
'''
def main_domain_run_button(asset,asset_type,asset_id,project_id,project_name):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")
    try:

        '''
            判断子域名收集模块是否执行过
        '''
        sql ="select *  from module_function where  asset_type=%d and asset_id=%d and project_id=%d"%(int(asset_type),int(asset_id),int(project_id))
        cursor.execute(sql)
        subdomain_had_execute_results = cursor.fetchall()
        if len(subdomain_had_execute_results) >0:
            for module_function in subdomain_had_execute_results:
                if module_function:
                    id = module_function[0]
                    module_name =module_function[1]
                    module_status =module_function[2]
                    old_task_id = module_function[8]
                    if module_name ==SUBDOMAIN_MODULE:
                        '''
                            重新运行oneforall模块,不是运行中
                        '''
                        if module_status !=1 or module_status !="1":
                            oneforall_task = run_oneforall_module.delay(asset,asset_type,asset_id,project_id,project_name)
                            task_id = oneforall_task.id
                            update_sql ="update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d"%(task_id,old_task_id,int(id))
                            cursor.execute(update_sql)
                            redis_connection.lpush(DOMAIN_TASK_LIST, task_id)
                            logger.log("oneforall更新模块时推送task_list %s"%task_id)

                    elif module_name ==CDN_MODULE:
                        '''
                            重置cdn模块
                        '''
                        if module_status !=1 or module_status !="1":
                            cdn_task = run_cdn_module.delay(asset,asset_type,asset_id,project_id,project_name)
                            cdn_task_id = cdn_task.id
                            update_sql ="update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d"%(cdn_task_id,old_task_id,int(id))
                            cursor.execute(update_sql)
                            redis_connection.lpush(DOMAIN_TASK_LIST, cdn_task_id)
                            logger.log("cdn更新模块时推送task_list %s" % cdn_task_id)
                    elif module_name ==WHOIS_INFO_MODULE:
                        if module_status != 1 or module_status != "1":
                            whois_info_task = run_whois_info.delay(asset,asset_type,asset_id,project_id,project_name)
                            whois_info_task_id = whois_info_task.id
                            update_sql = "update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d" % (
                            whois_info_task_id, old_task_id, int(id))
                            cursor.execute(update_sql)
                            redis_connection.lpush(DOMAIN_TASK_LIST, whois_info_task_id)
                            logger.log("whois_info更新模块时推送task_list %s" % whois_info_task_id)
            if cursor:
                cursor.close()
            return True

        else:
            '''
                没有执行过,插入模功能,放进队列
            '''
            oneforall_task =run_oneforall_module.delay(asset,asset_type,asset_id,project_id,project_name)
            task_id = oneforall_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (SUBDOMAIN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1,task_id)
            logger.log(insert_sql)
            cursor.execute(insert_sql)
            redis_connection.lpush(DOMAIN_TASK_LIST, task_id)
            logger.log("oneforall模块推送task_list %s" % task_id)
            '''
                执行cdn模块
            '''
            cdn_task = run_cdn_module.delay(asset,asset_type,asset_id,project_id,project_name)
            cdn_task_id = cdn_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                CDN_MODULE, 1,int(asset_type), int(asset_id), int(project_id), 1, cdn_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(DOMAIN_TASK_LIST, cdn_task_id)
            logger.log("cdn模块推送task_list %s" % cdn_task_id)
            '''
                执行whois_info
            '''
            whois_info_task = run_whois_info.delay(asset,asset_type,asset_id,project_id,project_name)
            whois_info_task_id = whois_info_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                WHOIS_INFO_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, whois_info_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(DOMAIN_TASK_LIST, whois_info_task_id)
            logger.log("whois_info模块推送task_list %s" % whois_info_task_id)
            if cursor:
                cursor.close()
            return True
    except Exception as e:
        logger.log("主域名运行按钮出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False

'''
    子域名运行按钮逻辑
'''
def subdomain_run_button(asset,asset_type,asset_id,project_id,project_name):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        '''
            执行cdn模块
        '''
        logger.log("subdomain button is on")
        sql = "select * from module_function where asset_type=%d and asset_id=%d and project_id=%d" % (
        int(asset_type), int(asset_id), int(project_id))
        logger.log(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        logger.log("subdomain run button=="+str(results))
        if len(results) >0:
              for result in results:
                id = result[0]
                module_name = result[1]
                module_status=result[2]
                old_task_id=result[8]
                if module_name ==CDN_MODULE:
                    if module_status != 1 or module_status != "1":
                        '''
                            重新运行cdn判断模块
                        '''
                        cdn_task = run_cdn_module.delay(asset,asset_type,asset_id,project_id,project_name)
                        cdn_task_id = cdn_task.id
                        update_sql = "update module_function set module_status=1,module_log='',fail_reason='',task_id='%s' where task_id='%s' and id=%d" % (
                        cdn_task_id, old_task_id,int(id))
                        logger.log("update sql =="+str(update_sql))
                        cursor.execute(update_sql)
                        redis_connection.lpush(DOMAIN_TASK_LIST, cdn_task_id)
                        logger.log("cdn模块更新时推送task_list %s" % cdn_task_id)


              if cursor:
                  cursor.close()
              return True


        else:
            logger.log("subdomain not beginning")
            cdn_task = run_cdn_module.delay(asset,asset_type,asset_id,project_id,project_name)
            cdn_task_id = cdn_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                CDN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, cdn_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(DOMAIN_TASK_LIST, cdn_task_id)
            logger.log("cdn模块推送task_list %s" % cdn_task_id)
            if cursor:
                cursor.close()
            return True
    except Exception as e:
        logger.log("执行子域名运行按钮出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False



'''
    执行端口探测
'''
def run_port_rustscan(asset,asset_type,asset_id,project_id,project_name):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")

    try:
        portscan_task = port_scanner.delay(asset,asset_type,asset_id,project_id,project_name)
        portscan_task_id = portscan_task.id
        '''
            插入一条模块状态记录
        '''
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id) values('%s',%d,%d,%d,%d,'%s')" % (
            PORT_SCAN_MODULE, asset_type, asset_id, project_id, 1, portscan_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, portscan_task_id)
        logger.log("端口扫描模块推送task_list %s" % portscan_task_id)
        if cursor:
            cursor.close()
        return True
    except Exception as e:
        logger.log("执行端口扫描任务出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False

'''
    ip运行按钮
'''
def ip_run_button(asset,asset_type,asset_id,project_id,project_name):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        sql = "select * from module_function where  asset_type=%d and asset_id=%d and project_id=%d and module_name in ('%s','%s','%s') "  % (
            int(asset_type), int(asset_id), int(project_id),SIDE_STATIONS_MODULE,CRANGE_MODULE,IP_LOCATION_MODULE)
        logger.log("ip run button =="+str(sql))
        cursor.execute(sql)
        results = cursor.fetchall()
        if len(results )>0:
            '''
                更新状态
            '''
            for result in results:
                id=result[0]
                module_name = result[1]
                module_status = result[2]
                old_task_id = result[8]
                if module_name ==SIDE_STATIONS_MODULE:
                    if module_status !=1 and module_status !="1":
                        run_side_stations_task = run_side_stations.delay(asset,asset_type,asset_id,project_id,project_name)
                        side_stations_task_id = run_side_stations_task.id
                        redis_connection.lpush(IP_TASK_LIST, side_stations_task_id)
                        logger.log("旁站模块更新时推送task_list %s" % side_stations_task_id)
                        update_sql = "update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d" % (
                            side_stations_task_id, old_task_id, int(id))
                        cursor.execute(update_sql)

                elif module_name ==CRANGE_MODULE:
                    if module_status !=1 and module_status !="1":
                        run_crange_task = run_crange.delay(asset,asset_type,asset_id,project_id,project_name)
                        crange_task_id = run_crange_task.id
                        update_sql = "update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d" % (
                            crange_task_id, old_task_id, int(id))
                        cursor.execute(update_sql)
                        redis_connection.lpush(IP_TASK_LIST, crange_task_id)
                        logger.log("C段拓展模块更新时推送task_list %s" % crange_task_id)
                elif module_name ==IP_LOCATION_MODULE:
                    if module_status != 1 and module_status != "1":
                        run_ip_location_task = run_ip_location.delay(asset,asset_type,asset_id,project_id,project_name)
                        ip_location_task_id = run_ip_location_task.id
                        update_sql = "update module_function set module_status=1,module_log='',fail_reason='',task_id=%s where task_id=%s and id=%d" % (
                            ip_location_task_id, old_task_id, int(id))
                        cursor.execute(update_sql)
                        redis_connection.lpush(IP_TASK_LIST, ip_location_task_id)
                        logger.log("IP地理位置模块更新时推送task_list %s" % ip_location_task_id)
            if cursor:
                cursor.close()
            return True
        else:
            '''
                加入任务队列
            '''
            run_side_stations_task = run_side_stations.delay(asset,asset_type,asset_id,project_id,project_name)
            side_stations_task_id = run_side_stations_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                CDN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, side_stations_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(IP_TASK_LIST, side_stations_task_id)
            logger.log("旁站模块推送task_list %s" % side_stations_task_id)
            run_crange_task = run_crange.delay(asset,asset_type,asset_id,project_id,project_name)
            crange_task_id =run_crange_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                CDN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, crange_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(IP_TASK_LIST, crange_task_id)
            logger.log("C段拓展模块推送task_list %s" % crange_task_id)
            run_ip_location_task = run_ip_location.delay(asset,asset_type,asset_id,project_id,project_name)
            ip_location_task_id = run_ip_location_task.id
            insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
                CDN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, ip_location_task_id)
            cursor.execute(insert_sql)
            redis_connection.lpush(IP_TASK_LIST, ip_location_task_id)
            logger.log("IP地理位置模块推送task_list %s" % ip_location_task_id)
            if cursor:
                cursor.close()
            return True
    except Exception as e:
        logger.log("ip运行按钮出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False



'''
    c段ip运行按钮,串行执行
'''
def crange_run_button(asset,asset_type,asset_id,project_id,project_name):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        ip_location_task =run_ip_location.delay(asset,asset_type,asset_id,project_id,project_name)
        ip_location_task_id = ip_location_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            CDN_MODULE,1, int(asset_type), int(asset_id), int(project_id), 1, ip_location_task_id)

        cursor.execute(insert_sql)
        redis_connection.lpush(IP_TASK_LIST, ip_location_task_id)
        logger.log("IP地理位置模块推送task_list %s" % ip_location_task_id)
        if cursor:
            cursor.close()
        return True
    except Exception as e:
        logger.log("c段ip运行按钮出现异常==="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False




'''
   非web端口运行按钮 
'''
def run_port_banner_scan(asset,asset_type,asset_id,project_id,project_name,port):
    cursor =connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        port_banner_task =port_banner_scan.delay(asset,asset_type,asset_id,project_id,project_name,port)
        port_banner_task_id = port_banner_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            PORT_SCAN_MODULE,1, asset_type, asset_id, project_id, 1, port_banner_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, port_banner_task_id)
        logger.log("端口banner探测模块推送task_list %s" % port_banner_task_id)
        if cursor:
            cursor.close()
        return True
    except Exception as e:
        logger.log("执行非web端口运行按钮出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False


'''
    http端口
'''
def run_http_port(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type):
    cursor=connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        # params ={
        #     "asset":asset,
        #     "asset_id":asset_id,
        #     "asset_type":asset_type,
        #     "project_id":project_id,
        #     "project_name":project_name,
        #     "port":port
        # }
        run_web_asset_task = web_recongnize.delay(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type)
        run_web_asset_task_id = run_web_asset_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            WEB_ASSET_RECONGNIZE_MODULE,1, asset_type, asset_id, project_id, 1, run_web_asset_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, run_web_asset_task_id)
        logger.log("web资产扫描模块推送task_list %s" % run_web_asset_task_id)
        screenshot_task=screenshot.delay(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type)
        screenshot_task_id =screenshot_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            SCREENSHOT_MODULE,1, asset_type, asset_id, project_id, 1, screenshot_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, screenshot_task_id)
        logger.log("web截图模块推送task_list %s" % screenshot_task_id)
        if cursor:
            cursor.close()
        return True

    except Exception as e:
        logger.log("执行http端口出现异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False


'''
    ssl端口运行逻辑
'''
def run_ssl_port(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type):
    cursor = connection.cursor()
    redis_connection =get_redis_connection("default")
    try:
        # params = {"asset": asset, "asset_id": asset_id, "asset_type": asset_type, "project_id": project_id,
        #           "project_name": project_name, "port": port, "module_name": WEB_ASSET_RECONGNIZE_MODULE}

        run_web_asset_task = web_recongnize.delay(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type)
        run_web_asset_task_id = run_web_asset_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            WEB_ASSET_RECONGNIZE_MODULE,1, asset_type, asset_id, project_id, 1, run_web_asset_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST,run_web_asset_task_id)
        logger.log("web资产识别模块推送task_list %s" % run_web_asset_task_id)
        # params["module_name"] = SCREENSHOT_MODULE
        screenshot_task = screenshot.delay(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type)
        screenshot_task_id = screenshot_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            SCREENSHOT_MODULE,1, asset_type, asset_id, project_id, 1, screenshot_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, screenshot_task_id)
        logger.log("屏幕截图模块推送task_list %s" % screenshot_task_id)
        # params["module_name"] = SSLINFO_MODULE
        ssl_info_task = sslinfo.delay(asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type)
        ssl_info_task_id=ssl_info_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            SSLINFO_MODULE,1, asset_type, asset_id, project_id, 1, ssl_info_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, ssl_info_task_id)
        logger.log("SSL模块推送task_list %s" % ssl_info_task_id)
        if cursor:
            cursor.close()
        return True
    except Exception as e:
        logger.log("执行http端口出现异常==" + str(e.__str__()))
        if cursor:
            cursor.close()

        return False


'''
    非web端口运行
'''
def run_not_web_service_button(asset,asset_type,asset_id,project_id,project_name,port):
    cursor = connection.cursor()
    try:
        redis_connection=get_redis_connection("default")
        # params = {
        #     "asset": asset,
        #     "asset_id": asset_id,
        #     "asset_type": asset_type,
        #     "project_id": project_id,
        #     "project_name": project_name,
        #     "port": port,
        #     "module_name":PORT_BANNER_MODULE
        # }
        run_web_asset_task = port_banner_scan.delay(asset,asset_type,asset_id,project_id,project_name,port)
        run_web_asset_task_id = run_web_asset_task.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            PORT_BANNER_MODULE,1, asset_type, asset_id, project_id, 1, run_web_asset_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST,run_web_asset_task_id)
        logger.log("端口banner模块推送task_list %s" % run_web_asset_task_id)
        if cursor:
            cursor.close()
        return True
    except Exception as e:
        logger.log("运行非web端口异常=="+str(e.__str__()))
        if cursor:
            cursor.close()
        return False



'''
    asset,asset_type,service_id,project_id,project_name,port,domain,srv_type
'''
def run_dirbuster_button(asset,asset_type,service_id,project_id,project_name,port,domain,srv_type):
    cursor = connection.cursor()
    try:
        redis_connection = get_redis_connection("default")
        dirbuster = dirbuster_task.delay(asset, asset_type, service_id, project_id, project_name, port,domain,srv_type)
        dirbuster_task_id = dirbuster.id
        insert_sql = "insert into module_function(module_name,module_status,asset_type,asset_id,project_id,task_status,task_id,create_time,update_time) values('%s',%d,%d,%d,%d,%d,'%s',now(),now())" % (
            DIRBUSTER_MODULE, 1, int(asset_type), int(service_id), int(project_id), 1, dirbuster_task_id)
        cursor.execute(insert_sql)
        redis_connection.lpush(SERVICE_TASK_LIST, dirbuster_task_id)
        logger.log("目录爆破模块推送task_list %s" % dirbuster_task_id)
        if cursor:
            cursor.close()
        return True

    except Exception as e:
        logger.log("运行非web端口异常==" + str(e.__str__()))
        if cursor:
            cursor.close()
        return False





























