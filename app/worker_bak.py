#!/usr/bin/python3 env
# -*- coding:UTF-8 -*-
__author__ = "15919"
# project name worker
__time__ = "2021/6/9 14:51"
from django.db import connection
import time
from .tasks import ip_run_button,crange_run_button,subdomain_run_button,run_port_banner_scan,run_http_port,run_ssl_port,run_dirbuster_button
from django_redis import get_redis_connection
from background_task import background
from marmo.settings import TASK_LIST
from celery.result import AsyncResult
from app.dao.module_function import ModuleFunctionDao
import json
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
'''
    后台redis任务
'''
@background
def module_function_timing():
    connection = get_redis_connection("default")
    modulefunctiondao = ModuleFunctionDao()
    try:
        last_len = connection.llen(TASK_LIST)
        logger.log("module_function timing === "+str(last_len))
        if last_len >0:
            task_id = connection.rpop(TASK_LIST)

            if task_id:
                task_id = task_id.decode(encoding="UTF-8")
                logger.log("task_id===" + str(task_id))
                task_result = AsyncResult(id=task_id)
                is_ready =task_result.ready()
                state = task_result.state
                logger.log("is_ready=="+str(is_ready))
                logger.log(("state===="+str(state)))
                if is_ready and state =="SUCCESS":
                    result = task_result.result
                    logger.log("result =="+str(result))
                    if result:
                        result = json.loads(result)
                        asset_id =""
                        project_id =""
                        module_name=""
                        asset_type=""
                        if result.__contains__("asset_id"):
                            asset_id=result["asset_id"]
                        if result.__contains__("project_id"):
                            project_id=result["project_id"]
                        if result.__contains__("asset_type"):
                            asset_type=result["asset_type"]
                        if result.__contains__("module_name"):
                            module_name=result["module_name"]
                        if asset_id and project_id and module_name and asset_type:
                            update_params ={
                                "asset_id":asset_id,
                                "project_id":project_id,
                                "asset_type":asset_type,
                                "module_name":module_name
                            }
                            if result.__contains__["exists_data"]:
                                exists_data = result["exists_data"]
                                if exists_data: #存在数据
                                    update_params["module_log"]=result["data"]
                                else:
                                    update_params["module_log"]=""
                            if result.__contains__["status_code"]:
                                status_code = result["status_code"]
                                if status_code ==3:
                                    update_params["fail_reason"]=result["fail_reason"]
                                update_params["module_status"]=status_code
                            modulefunctiondao.update_module_function(update_params)
                else:
                   connection.lpush(TASK_LIST,task_id)
    except Exception as e:
        print("获取任务结果出现异常=="+str(e.__str__()))



'''
    子域名定时器
    条件:celery_status:1
    domain_type:2
    传入的参数:domain_id,asset_type,project_id,project_name
    只查运行中的项目
'''
@background
def sub_domain_timing():
    print("子域名定时器执行")
    cursor =connection.cursor()
    is_done=False
    try:
        redis_connection = get_redis_connection("default")
        logger.log("sub domain timing")
        project_sql = "select name from marmo_project where status=1 "
        print(project_sql)
        cursor.execute(project_sql)
        project_results = cursor.fetchall()
        print("子域名查询启动项目="+str(project_results))
        if project_results and len(project_results) >= 1:
            for project in project_results:
                name = project[0]
                sub_domain = redis_connection.hget(name,"sub_domain")
                if sub_domain:
                    sub_domain = sub_domain.decode(encoding="UTF-8")
                if sub_domain ==2 or sub_domain =="2":
                    continue
                if redis_connection.hexists(name, "main_domain"):
                    port_rustscan = redis_connection.hget(name, "main_domain")

                    if isinstance(port_rustscan,bytes):
                        port_rustscan = port_rustscan.decode(encoding="UTF-8")
                    print(port_rustscan)
                    if port_rustscan == 2 or port_rustscan == "2":
                        '''
                            说明主域名已经全部完成操作,查出所有的子域名放入队列中
                        '''
                        # count=0
                        # while True:
                        #     if count>=5:
                        #         logger.log("子域名完成操作")
                        #         redis_connection.hset(name,"sub_domain",2)
                        #         break
                        sql ="select domain.id,domain.domain_name,domain.project_id,project.name project_name from online_asset_domain domain,marmo_project project where domain.project_id=project.id and domain.celery_status=0 and domain.domain_type=2 and project.status=1 "
                        print(sql)
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        print("子域名结果=="+str(results))
                        if results and len(results) >=1:
                            for result in results:
                                asset_id = result[0]
                                asset = result[1]
                                project_id = result[2]
                                project_name = result[3]
                                subdomain_run_button(asset,1,asset_id,project_id,project_name)
                                '''
                                    更新当前任务的celery_status状态
                                '''
                                update_celery_status_sql ="update online_asset_domain set celery_status=1 where domain_name='%s' and id=%d"%(asset,asset_id)
                                logger.log(update_celery_status_sql)
                                cursor.execute(update_celery_status_sql)

                        else:
                            logger.log("子域名完成操作")
                            redis_connection.hset(name, "sub_domain", 2)
    except Exception as e:
        print("子域名定时器出现异常==="+str(e.__str__()))
    finally:
        if cursor:
            cursor.close()



'''
    ip定时器
    ip类型:真实ip,c段ip
'''
@background
def ip_timing():
    cursor = connection.cursor()
    try:
        logger.log("ip timing start ")
        redis_connection = get_redis_connection("default")
        project_sql = "select name from marmo_project where status=1 "
        logger.log(project_sql)
        cursor.execute(project_sql)
        project_results = cursor.fetchall()
        logger.log("project result =="+str(project_results))
        if project_results and len(project_results) >= 1:
            for project in project_results:
                name = project[0]
                logger.log(name)
                ip_value = redis_connection.hget(name, "ip")
                logger.log("ip_value===="+str(ip_value))
                if ip_value:
                    ip_value =ip_value.decode(encoding="UTF-8")
                if ip_value ==2 or ip_value =="2":
                    continue
                if redis_connection.hexists(name, "sub_domain"):
                    port_rustscan = redis_connection.hget(name, "sub_domain")
                    if port_rustscan:
                        port_rustscan = port_rustscan.decode(encoding="UTF-8")
                    logger.log("sub domain is finished =="+str(port_rustscan))
                    if port_rustscan == 2 or port_rustscan == "2":
                        # count=0
                        # while True:
                        #     if count>=10:
                        #         redis_connection.hset(name,"ip",2)
                        #         is_done=True
                        sql ="select ip.id,ip.ip_type,ip.project_id,ip.ip,project.name project_name from online_asset_ip ip,marmo_project project where ip.project_id=project.id and ip.celery_status=0 and project.status=1 and ip.ip_type in (1,4) "
                        cursor.execute(sql)
                        logger.log(sql)
                        results = cursor.fetchall()
                        logger.log("ip results==="+str(results))
                        if results and len(results) >= 1:
                            for result in results:
                                asset_id = result[0]
                                ip_type =result[1]
                                project_id =result[2]
                                asset = result[3]
                                project_name = result[4]
                                if ip_type ==1:
                                    '''
                                        真实ip
                                        asset,asset_type,asset_id,project_id,project_name
                                    '''
                                    logger.log("运行真实ip逻辑")
                                    ip_run_button(asset,2,asset_id,project_id,project_name)

                                elif ip_type ==4:
                                    '''
                                       c段ip 
                                    '''
                                    logger.log("运行c段IP逻辑")
                                    crange_run_button(asset,2,asset_id,project_id,project_name)
                                '''
                                    投送任务后修改当前ip的状态为待端口探测的状态
                                '''
                                update_sql ="update online_asset_ip set celery_status=5 where id=%d and ip='%s'"%(asset_id,asset)
                                cursor.execute(update_sql)
                        else:
                            redis_connection.hset(name, "ip", 2)
                            logger.log("ip 数据已经全部完成")
    except Exception as e:
        print("ip定时器出现异常=="+str(e.__str__()))
    finally:
        if cursor:
            cursor.close()

'''
    端口banner定时器
'''
@background
def service_banner_timing():
    cursor = connection.cursor()
    try:
        logger.log("service banner timing")
        redis_connection = get_redis_connection("default")
        project_sql = "select name from marmo_project where status=1 "
        cursor.execute(project_sql)
        project_results = cursor.fetchall()
        logger.log("service banner results =="+str(project_results))
        if project_results and len(project_results) >= 1:
            for project in project_results:
                name = project[0]
                banner = redis_connection.hget(name,"banner")
                if banner:
                    banner =banner.decode(encoding="UTF-8")
                if banner ==2 or banner =="2":
                    continue
                if redis_connection.hexists(name, "port_rustscan"):
                    port_rustscan = redis_connection.hget(name, "port_rustscan")
                    if port_rustscan:
                        port_rustscan = port_rustscan.decode(encoding="UTF-8")
                    if port_rustscan == 2 or port_rustscan == "2":
                        '''
                            完成了端口探测之后执行banner探测
                        '''
                        sql = "select service.id,service.port,service.srv_type,service.asset,service.asset_type,service.project_id,project.name project_name from online_asset_service service,marmo_project project where service.project_id=project.id and service.celery_status=6 and project.status=1"
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        if results and len(results) >= 1:
                            for result in results:
                                asset_id = result[0]
                                port = result[1]
                                srv_type=result[2]
                                asset = result[3]
                                project_id = result[5]
                                project_name = result[6]
                                if srv_type ==0:
                                    '''
                                        只进行banner探测,celery任务状态不更新
                                        asset,asset_type,asset_id,project_id,project_name,port
                                    '''
                                    run_port_banner_scan(asset,3,asset_id,project_id,project_name,port)
                                    '''
                                        修改状态为待端口运行
                                    '''
                                    update_sql ="update online_asset_service set celery_status=5 where port='%s' and id=%d"%(port,asset_id)
                                    cursor.execute(update_sql)

                        else:
                            logger.log("端口banner全部完成")
                            redis_connection.hset(name, "banner", 2)

    except Exception as e:
        print("ip定时器出现异常==" + str(e.__str__()))
    finally:
        if cursor:
            cursor.close()


'''
    端口定时器:
    执行时机:完成banner探测任务
    完成端口banner探测之后的定时器
    遍历service表，找出http/https类型的端口,查找该端口关联的ip,如果ip有关联域名，则要查出域名，否则查找ip就行了
'''
@background
def service_timing():
    cursor = connection.cursor()
    try:
            logger.log("service timing")
            redis_connection = get_redis_connection("default")
            project_sql = "select name from marmo_project where status=1 "
            logger.log("service timing sql=="+str(project_sql))
            cursor.execute(project_sql)
            project_results = cursor.fetchall()
            logger.log("service timing results=="+str(project_results))
            if project_results and len(project_results) >= 1:
                for project in project_results:
                    name = project[0]
                    service = redis_connection.hget(name,"service")
                    if service:
                        service =service.decode(encoding="UTF-8")
                    if service ==2 or service =="2":
                        continue
                    if redis_connection.hexists(name, "port_rustscan"):
                        port_rustscan = redis_connection.hget(name, "port_rustscan")
                        if port_rustscan:
                            port_rustscan = port_rustscan.decode(encoding="UTF-8")
                        if port_rustscan == 2 or port_rustscan == "2":
                                sql = "select service.id,service.port,service.srv_type,service.asset,service.asset_type,service.project_id,project.name project_name from online_asset_service service,marmo_project project where service.project_id=project.id and service.celery_status=5 and project.status=1"
                                logger.log(sql)
                                cursor.execute(sql)
                                results = cursor.fetchall()
                                logger.log("service timing results ==="+str(results))
                                if results and len(results) >= 1:
                                    for result in results:
                                        service_id = result[0]
                                        port = result[1]
                                        srv_type=result[2]
                                        asset = result[3]
                                        project_id = result[5]
                                        project_name = result[6]
                                        '''
                                            根据asset查询ip对应的资产信息，关联的是域名还是ip,如果关联域名要把域名查询出来
                                        '''
                                        domain =""
                                        if asset:
                                            ip_sql ="select id,source_detail from online_asset_ip ip where ip.ip='%s' limit 1"%(asset)
                                            cursor.execute(ip_sql)
                                            ip_results = cursor.fetchall()
                                            if ip_results and len(ip_results) >=1:
                                                for ip_result in ip_results:
                                                    ip_id = ip_result[0]
                                                    '''
                                                        查询ip有没有对应的域名
                                                    '''
                                                    ip_domain_sql = "select domain.domain_name from online_asset_domain domain,domain_ip_relation dir where domain.id=dir.asset_domain_id and dir.asset_ip_id=%d limit 1;"%(int(ip_id))
                                                    cursor.execute(ip_domain_sql)
                                                    ip_domain_results = cursor.fetchall()
                                                    if ip_domain_results and len(ip_domain_results) >=1:
                                                        for ip_domain_result in ip_domain_results:
                                                            domain = ip_domain_result[0]
                                        if srv_type == 1:
                                            '''
                                                http端口
                                                asset,asset_type,asset_id,project_id,project_name,port
                                            '''
                                            run_http_port(asset,3,service_id,project_id,project_name,port,domain,"http")

                                        elif srv_type == 2:
                                            '''
                                                https端口
                                                asset,asset_type,asset_id,project_id,project_name,port
                                            '''
                                            run_ssl_port(asset,3,service_id,project_id,project_name,port,domain,"https")
                                        '''
                                            更新资产状态为待目录爆破
                                        '''
                                        update_sql ="update online_asset_service set celery_status=7 where port=%d and id=%d"%(int(port),int(service_id))
                                        cursor.execute(update_sql)
                                        logger.log("更新资产信息")
                                else:
                                    redis_connection.hset(name, "service", 2)
    except Exception as e:
        print("ip定时器出现异常==" + str(e.__str__()))
    finally:
        if cursor:
            cursor.close()


'''
    端口探测执行定时器,查找状态是5的ip记录,状态5是那些已经完成了ip地理位置，旁站拓展，C段扫描
'''
@background
def port_scan_timing():
    from app.module import PortScan
    from marmo.settings import PORT_SCAN_MODULE
    cursor = connection.cursor()
    try:
        logger.log("port scan timing")
        redis_connection = get_redis_connection("default")
        project_sql ="select name from marmo_project where status=1 "
        cursor.execute(project_sql)
        project_results = cursor.fetchall()
        logger.log("port scan results =="+str(project_results))
        if project_results and len(project_results) >=1:
            for project in project_results:
                name = project[0]
                port_rustscan = redis_connection.hget(name,"port_rustscan")
                if port_rustscan:
                    port_rustscan = port_rustscan.decode(encoding="UTF-8")
                if port_rustscan ==2 or port_rustscan =="2":
                    '''
                        端口探测已经完成
                    '''
                    logger.log("%s 已经完成端口探测"%name)
                    continue
                if redis_connection.hexists(name,"ip"):
                    is_ip_done = redis_connection.hget(name,"ip")
                    if is_ip_done:
                        is_ip_done = is_ip_done.decode(encoding="UTF-8")
                    if is_ip_done ==2 or is_ip_done =="2":
                        '''
                            代表ip已经全部弄完，可以进行端口探测
                        '''

                        sql = "select ip.id,ip.ip_type,ip.project_id,ip.ip,project.name project_name from online_asset_ip ip,marmo_project project where ip.project_id=project.id and ip.celery_status=5 and project.status=1 and ip.ip_type in (1,4)"
                        logger.log("port scan sql=="+str(sql))
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        logger.log("port scan results =="+str(results))
                        if results and len(results) >= 1:
                            for result in results:
                                asset_id = result[0]
                                ip_type = result[1]
                                project_id = result[2]
                                asset = result[3]
                                project_name = result[4]
                                '''
                                asset,asset_type,asset_id,project_id,project_name
                                理论上端口探测不允许后台任务执行，只能前台运行
                                '''
                                # run_port_rustscan(asset,3,asset_id,project_id,project_name)
                                logger.log("%s 进行端口探测")
                                port_scan = PortScan({"asset": asset, "asset_type": 3, "asset_id": asset_id,
                                                      "project_id": project_id, "module_name": PORT_SCAN_MODULE,
                                                      "project_name": project_name,"type":ip_type})
                                port_scan.run()
                                '''
                                    修改状态为端口探测已经完成
                                '''
                                update_sql ="update online_asset_ip set celery_status=6 where ip='%s' and id=%d"%(asset,asset_id)
                                cursor.execute(update_sql)
                        else:
                            redis_connection.hset(name, "port_rustscan", 2)
    except Exception as e:
        print("执行端口探测定时器出现异常=="+str(e.__str__()))
    finally:
        if cursor:
            cursor.close()


'''
    c段ip进行出口诊断,这个任务会一直持续执行
'''
@background
def crange_ip_location_timing():
    cursor = connection.cursor()
    try:
        logger.log("ip地理位置定时器")
        query_sql ="select ip.id,ip.ip_type,ip.project_id,ip.ip,project.name project_name from online_asset_ip ip,marmo_project project where ip.project_id=project.id and ip.celery_status=7 and project.status=1 and ip.ip_type=4 "
        logger.log(query_sql)
        cursor.execute(query_sql)
        results = cursor.fetchall()
        if results and len(results) >= 1:
            for result in results:
                asset_id = result[0]
                project_id = result[2]
                asset = result[3]
                project_name = result[4]
                '''
                    asset,asset_type,asset_id,project_id,project_name
                '''
                crange_run_button(asset,2,asset_id,project_id,project_name)
                '''
                    更新c段IP的状态为待端口探测
                '''
                update_sql = "update online_asset_ip set celery_status=5 where id=%d and ip='%s'" % (asset_id, asset)
                cursor.execute(update_sql)

    except Exception as e:
        logger.log("ip地理位置定时器出现异常==="+str(e.__str__()))

    finally:
        if cursor:
            cursor.close()



'''
    开始进行目录爆破
    查找端口-查找ip-查找域名-
'''
@background
def dirbuster_timing():
    cursor = connection.cursor()
    redis_connection = get_redis_connection("default")
    try:
        logger.log("dirbuster timing")
        project_sql = "select name from marmo_project where status=1 "
        logger.log("dirbuster timing sql==" + str(project_sql))
        cursor.execute(project_sql)
        project_results = cursor.fetchall()
        logger.log("dirbuster timing results==" + str(project_results))
        if project_results and len(project_results) >= 1:
            for project in project_results:
                name = project[0]
                dirbuster = redis_connection.hget(name, "dirbuster")
                if dirbuster:
                    dirbuster = dirbuster.decode(encoding="UTF-8")
                if dirbuster == 2 or dirbuster == "2":
                    '''
                        已经完成目录爆破
                    '''
                    continue
                if redis_connection.hexists(name, "service"):
                    service = redis_connection.hget(name, "service")
                    if service:
                        service = service.decode(encoding="UTF-8")
                    if service == 2 or service == "2":
                        sql = "select service.id,service.port,service.srv_type,service.asset,service.asset_type,service.project_id,project.name project_name from online_asset_service service,marmo_project project where service.project_id=project.id and service.celery_status=7 and project.status=1 and service.srv_type in (1,2)"
                        logger.log(sql)
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        logger.log("dirbuster service timing ===" + str(results))
                        if results and len(results) >= 1:
                            for result in results:
                                service_id = result[0]
                                port = result[1]
                                srv_type = result[2]
                                asset = result[3]
                                project_id = result[5]
                                project_name = result[6]
                                '''
                                    根据asset查询ip对应的资产信息，关联的是域名还是ip,如果关联域名要把域名查询出来
                                '''
                                domain = ""
                                if asset:
                                    ip_sql = "select id,source_detail from online_asset_ip ip where ip.ip='%s' limit 1" % (
                                        asset)
                                    cursor.execute(ip_sql)
                                    ip_results = cursor.fetchall()
                                    if ip_results and len(ip_results) >= 1:
                                        for ip_result in ip_results:
                                            ip_id = ip_result[0]
                                            '''
                                                查询ip有没有对应的域名
                                            '''
                                            ip_domain_sql = "select domain.domain_name from online_asset_domain domain,domain_ip_relation dir where domain.id=dir.asset_domain_id and dir.asset_ip_id=%d limit 1;" % (
                                                int(ip_id))
                                            cursor.execute(ip_domain_sql)
                                            ip_domain_results = cursor.fetchall()
                                            if ip_domain_results and len(ip_domain_results) >= 1:
                                                for ip_domain_result in ip_domain_results:
                                                    domain = ip_domain_result[0]
                                protocol_type=""
                                if srv_type == 1:
                                    protocol_type="http"

                                elif srv_type == 2:
                                    protocol_type ="https"

                                run_dirbuster_button(asset, 3, service_id, project_id, project_name, port,
                                                     domain, protocol_type)
                                '''
                                    更新资产状态为
                                '''
                                update_sql = "update online_asset_service set celery_status=1 where port=%d and id=%d" % (
                                int(port), int(service_id))
                                cursor.execute(update_sql)
                                logger.log("更新资产信息")
                        else:
                            redis_connection.hset(name, "dirbuster", 2)
    except Exception as e:
        print("ip定时器出现异常==" + str(e.__str__()))
    finally:
        if cursor:
            cursor.close()




