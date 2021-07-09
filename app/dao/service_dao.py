# -*- coding:UTF-8 -*-
'''
    端口服务
'''
from app.models import OnlineAssetService,IpServiceRelation,ModuleFunction,MarmoProject,OnlineAssetIp,WebAsset
from app.utils.marmo_logger import Marmo_Logger
from django.db.models import Q
from django.db import connection
logger =Marmo_Logger()
import json
class ServiceDao():
    '''
            根据项目名称查询项目是否存在
        '''

    def query_project_exists_by_name(self, project_name):
        assert project_name
        try:
            project_obj = MarmoProject.objects.filter(name=project_name).get()
            return project_obj
        except MarmoProject.DoesNotExist:
            logger.log("新增域名项目不存在")
            raise Exception("新增域名项目不存在")
        except Exception as e:
            logger.log("query project exists " + str(e.__str__()))
            raise Exception("query project exists " + str(e.__str__()))
    '''
        查询非web端口
        查询条件:端口,关联ip,service_name
    '''
    def query_not_web_service(self,data):
        try:
            project_id =""
            if data.__contains__("project_id"):
                project_id =data["project_id"]
            if data.__contains__("project_name"):
                project_name = data["project_name"]
                if project_name:
                    project_obj = self.query_project_exists_by_name(project_name)
                    if project_obj:
                        project_id =project_obj.id
            if project_id:
                    page = data["page"]
                    limit = data["limit"]
                    page_start=(int(page)-1)*int(limit)
                    project_id = project_obj.id
                    query_args = {
                        "asset": data["asset"],
                        "project_id": int(project_id),
                        "srv_type": 9
                    }
                    if data.__contains__("port"):
                        query_args["port"]=data["port"]
                    if data.__contains__("service_name"):
                        query_args["service_name"]=data["service_name"]
                    web_results =OnlineAssetService.objects.filter(**query_args)
                    count = web_results.count()
                    web_result =web_results[page_start:int(limit)]
                    web_list =[]
                    if web_result:
                        for web in web_result:
                            web_obj ={}
                            web_obj["id"]=web.id
                            web_obj["port"]=web.port
                            web_obj["source"]=web.source
                            web_obj["asset"]=web.asset
                            web_obj["is_deep_http_recongnize"]=web.is_deep_http_recongnize
                            web_obj["service_name"]=web.service_name
                            '''
                                查询ip资产对应的功能模块
                            '''
                            module_function_results =ModuleFunction.objects.filter(**{
                                "project_id":int(query_args["project_id"]),
                                "asset_type":3,
                                "asset_id":int(web.id)
                            })[:]
                            temp_status =""
                            function_status_string =""
                            for function in module_function_results:
                                function_name = function.module_name
                                function_status = function.module_status
                                temp_status = ""
                                if function_status == 0:
                                    temp_status = "未开始"
                                elif function_status == 1:
                                    temp_status = "进行中"
                                elif function_status == 2:
                                    temp_status = "已结束"
                                    module_log = function.module_log
                                    if module_log:
                                        temp_status = "已结束(有数据)"
                                    else:
                                        temp_status = "已结束(无数据)"
                                elif function_status == 3:
                                    temp_status = "有异常"
                                function_status_string += function_name + " : " + temp_status + " ; "
                                web_obj["status"]=function_status_string
                                web_list.append(web_obj)

                    return web_list,count
        except Exception as e:
            logger.log("查询非web端口出现异常==="+str(e.__str__()))
            raise Exception("查询非web端口出现异常==="+str(e.__str__()))






    '''
        查询web端口
        查询条件:端口号,关联ip,module_name
        module_tag:name,version
        filter(~Q(srv_type=9))
        要区分是否有组件和版本
    '''
    def query_web_service(self,data):
        cursor = connection.cursor()
        try:
            project_name = data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    page = data["page"]
                    limit = data["limit"]
                    page_start = (int(page) - 1) * int(limit)
                    web_service_params={
                        "asset":data["asset"],
                        "project_id":int(project_id)
                    }
                    # if data.__contains__("port"):
                    #     web_service_params["port"]=data["port"]
                    # if data.__contains__("module_name"):
                    #     web_service_params["module_name"]=data["module_name"]
                    # if data.__contains__("module_version"):
                    #     web_service_params["version"]=data["module_version"]
                    select_sql ="""
                        select a.*,mp.name project_name from (SELECT
                            s.id,
                            s.PORT,
                            s.source,
                            s.source_detail,
                            s.srv_type,
                            s.asset,
                            s.is_deep_http_recongnize,
                            s.project_id             
                        FROM
                            online_asset_service s
                        WHERE 1=1
                            AND s.project_id =%d and (s.srv_type=1 or s.srv_type=2) and s.asset='%s'
                    """%(int(project_id),web_service_params["asset"])
                    # if web_service_params.__contains__("port"):
                    #     select_sql+=" and s.port="+web_service_params["port"]
                    # if web_service_params.__contains__("asset"):
                    #     select_sql+=" and s.asset='"+web_service_params["asset"]+"'"
                    # if web_service_params.__contains__("module_name"):
                    #     select_sql+=" and mt.module_name='"+web_service_params["module_name"]+"'"
                    # if web_service_params.__contains__("version"):
                    #     select_sql+=" and mt.version="+web_service_params["version"]
                    select_sql+=") a left join marmo_project mp on mp.id=a.project_id LIMIT %d,%d;"%(page_start,int(limit))
                    print(select_sql)
                    cursor.execute(select_sql)
                    web_results = cursor.fetchall()
                    web_list =[]
                    for web in web_results:
                        web_obj ={}
                        web_obj["id"]=web[0]
                        web_obj["port"]=web[1]
                        web_obj["source"]=web[2]
                        web_obj["source_detail"]=[3]
                        web_obj["srv_type"]=web[4]
                        web_obj["asset"]=web[5]
                        web_obj["is_deep_http_recongnize"]=web[6]

                        web_obj["project_id"] = web[7]

                        web_obj["project_name"] = web[8]
                        '''
                            查询web_asset表查看资产的web信息
                        '''
                        web_asset_sql ="select http_ssl_version,http_title,http_resp_body,http_resp_header,screenshot from web_asset where asset_id=%d and project_id=%d limit 1"%(web[0],web[7])
                        logger.log("service dao sql =="+str(web_asset_sql))
                        cursor.execute(web_asset_sql)
                        web_asset = cursor.fetchone()
                        logger.log("service dao asset results =="+str(web_asset))
                        if web_asset and len(web_asset) >=4:
                            web_obj["http_ssl_version"]=web_asset[0]
                            web_obj["http_title"]=web_asset[1]
                            web_obj["http_resp_header"]=web_asset[3]
                            web_obj["http_resp_body"] = web_asset[2]
                            web_obj["screenshot"] =web_asset[4]
                        else:
                            web_obj["http_ssl_version"] =""
                            web_obj["http_title"] =""
                            web_obj["http_resp_header"] =""
                            web_obj["http_resp_body"] =""
                            web_obj["screenshot"] =""
                        '''
                            查询ip资产对应的功能模块
                        '''
                        module_function_results = ModuleFunction.objects.filter(**{
                            "project_id": int(web_service_params["project_id"]),
                            "asset_type": 3,
                            "asset_id": int(web[0])
                        })[:]
                        temp_status = ""
                        temp_status_string =""
                        for function in module_function_results:
                            function_name = function.module_name
                            function_status = function.module_status
                            temp_status = ""
                            if function_status == 0:
                                temp_status = "未开始"
                            elif function_status == 1:
                                # function_obj["status"] = "进行中"
                                temp_status = "进行中"
                            elif function_status == 2:
                                # function_obj["status"] = "已结束"
                                temp_status = "已结束"
                                module_log = function.module_log
                                if module_log:
                                    # function_obj["status"]="已结束_有数据"
                                    temp_status = "已结束(有数据)"
                                else:
                                    temp_status = "已结束(无数据)"
                            elif function_status == 3:
                                # function_obj["status"] = "有异常"
                                temp_status = "有异常"
                            # function_list.append(function_obj)
                            temp_status_string += function_name + " : " + temp_status + " ; "
                            web_obj["status"]=temp_status_string
                        web_list.append(web_obj)
                    return web_list
        except Exception as e:
            logger.log("query_web_service出现异常==="+str(e.__str__()))
            raise Exception("query_web_service出现异常==="+str(e.__str__()))








    '''
        新增端口,有web，非web
        {port,description,asset,project_id}
    '''
    def create_service(self,data):
        try:
            project_name = data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    service_params ={
                        "port":int(data["port"]),
                        "description":data["description"],
                        "asset":data["asset"],
                        "srv_type":data["srv_type"],
                        "source":data["source"],
                        "project_id":int(project_id),
                        "source_detail":data["source_detail"],
                        "is_deep_http_recongnize":1,
                    }
                    '''
                        查询资产对应的id
                    '''
                    if data.__contains__("celery_status"):
                        service_params["celery_status"]=data["celery_status"]

                    else:
                        service_params["celery_status"]="9P"
                    if data.__contains__("is_deep_http_recongnize"):
                        service_params["is_deep_http_recongnize"] =data["is_deep_http_recongnize"]
                    else:
                        service_params["is_deep_http_recongnize"]="2"
                    if data.__contains__("asset_type"):
                        service_params["asset_type"]=data["asset_type"]
                    else:
                        service_params["asset_type"]=2
                    ip_obj = OnlineAssetIp.objects.filter(ip=service_params["asset"],project_id=int(project_id)).get()
                    if ip_obj:
                        ip_id = ip_obj.id
                        service = OnlineAssetService(port=service_params["port"],description=service_params["description"],asset=service_params["asset"],project_id=service_params["project_id"],srv_type=service_params["srv_type"],source=service_params["source"],celery_status=service_params["celery_status"],is_deep_http_recongnize=service_params["is_deep_http_recongnize"],asset_type=service_params["asset_type"])
                        service.save()

                        ip_service_relation = IpServiceRelation(asset_ip_id=int(ip_id),asset_service_id=int(service.id))
                        ip_service_relation.save()
                        '''
                        web端口要做的步骤
                        '''
                        if data["web_type"] =="web":
                            '''
                                创建web_asset记录
                            '''
                            web_asset_params ={
                                "url":"",
                                "status_code":0,
                                "source":1,
                                "source_detail":service_params["source_detail"],
                                "screenshot":'',
                                "asset_id":int(service.id),
                                "http_ssl_version":'',
                                "http_title":"",
                                "http_resp_body":'',
                                "http_resp_header":'',
                                "project_id":int(project_id),
                                "asset":service_params["asset"],
                                "asset_type":1,
                                "url_type":1
                            }
                            web_asset = WebAsset.objects.create(**web_asset_params)
                            if web_asset:
                                web_asset.save()
                        return True
        except OnlineAssetService.DoesNotExist:
            logger.log("新增端口关联资产ip不存在")
            raise Exception("新增端口关联资产ip不存在")
        except Exception as e:
            logger.log("新增端口出现异常=="+str(e.__str__()))
            raise Exception("新增端口出现异常=="+str(e.__str__()))


    '''
            查询loginfo，表事module_function
            project_id
            asset_id
            asset_type
        '''

    def query_log_info(self, data):
        try:
            log_info = ""
            module_function_result = ModuleFunction.objects.filter(project_id=int(data["project_id"]),
                                                                   asset_type=int(data["asset_type"]),
                                                                   asset_id=int(data["asset_id"]))[:]
            if module_function_result:
                for module_function in module_function_result:
                    module_name = module_function.module_name
                    module_log = module_function.module_log
                    start_log = ("*********" * 5) + str(module_name) + " start " + str("****" * 5)
                    log_info += start_log
                    log_info += ("-----------" * 10)
                    log_info += str(module_log)
                    end_log = ("*********" * 5) + str(module_name) + " end " + str("****" * 5)
                    log_info += end_log

            return log_info
        except Exception as e:
            raise Exception("查询log_info出现异常===" + str(e.__str__()))


    '''
        修改web端口信息,区分是web端口的修改还是非web端口的修改
        asset_id
        project_name
        port
        source
        source_detail
        releated
        domain
        banner
        version
         如果是web:
            srv_type
            is_deep_http_recongnize
            http_ssl_version
            http_response
            http_header
            
    '''
    def update_service(self,data):
        assert data["asset_id"]
        try:
            project_name = data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    service = OnlineAssetService.objects.filter(project_id=int(project_id),id=int(data["asset_id"])).get()
                    if service:
                        if data.__contains__("srv_type"):
                            service.srv_type =int(data["srv_type"])
                        if data.__contains__("port"):
                            service.port = int(data["port"])
                        if data.__contains__("source"):
                            service.source = data["source"]
                        if data.__contains__("source_detail"):
                            service.source_detail =data["source_detail"]
                        if data.__contains__("banner"):
                            service.service_name = data["banner"]
                        if data.__contains__("asset"): #
                            service.asset = data["asset"]
                        if data.__contains__("description"): #
                            service.description = data["description"]
                        if data.__contains__("version"):
                            service.service_version = data["version"]
                        service.save()




        except Exception as e:
            logger.log("更新web端口出现异常=="+str(e.__str__()))
            raise Exception("更新web端口出现异常=="+str(e.__str__()))

    '''
        修改非web端口信息
        update_not_web_params ={
                        "port":port,
                        "source":int(source),
                        "asset":asset,
                        "banner":banner,
                        "is_deep_http_recongnize":int(is_deep_http_recongnize),
                        "description":description
                    }
    '''
    def update_not_web_service(self,data):
            try:
                asset_id =""
                port =""
                if data.__contains__("asset_id"):
                    asset_id = data["asset_id"]
                if data.__contains__("port"):
                    port = data["port"]
                if asset_id and port:
                    '''
                        查找端口信息
                    '''
                    asset_service =OnlineAssetService.objects.filter(id=int(asset_id),port=int(port)).get()
                    if asset_service:
                        if data.__contains__("source"):
                            asset_service.source = int(data["source"])
                        if data.__contains__("asset"):
                            asset_service.asset = data["asset"]
                        if data.__contains__("banner"):
                            asset_service.service_name=data["banner"]
                        if data.__contains__("is_deep_http_recongnize"):
                            asset_service.is_deep_http_recongnize = int(data["is_deep_http_recongnize"])
                        asset_service.save()
                        return True
                else:
                    raise Exception("修改端口缺少id和port参数")
            except OnlineAssetService.DoesNotExist:
                logger.log("service 不存在 "+str(asset_id))
                raise Exception("修改端口不存在")

            except Exception as e:
                raise Exception("修改端口出现异常=="+str(e.__str__()))


    '''
        运行按钮
    '''
    def run_button(self,data):
        pass

    '''
        目录爆破按钮
    '''
    def dirbuster(self,data):
        cursor = connection.cursor()
        dirbuster_list = []
        try:
            asset =""
            project_name =""
            project_id =""

            if data.__contains__("asset"):
                asset = data["asset"]
            if data.__contains__("project_name"):
                project_name =data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id

            if project_id and asset:
                '''
                    查询ip资产表的爆破信息
                '''
                asset_ip_obj = OnlineAssetIp.objects.filter(ip=asset,project_id=int(project_id)).get()
                if asset_ip_obj:
                    dirbuster = asset_ip_obj.dirbuster
                    if dirbuster:
                        logger.log("dirbuster")
                        if "#@#" in dirbuster:
                            dirbuster_res =dirbuster.split("#@#")
                            for dirbuster_one in dirbuster_res:
                                if dirbuster_one and "[" in dirbuster_one and "]" in dirbuster_one:
                                    dirbuster_one = dirbuster_one.replace("'",'"')
                                    dirbuster_json = json.loads(dirbuster_one)
                                    for one in dirbuster_json:
                                        dirbuster_list.append(one)
                        else:
                            if dirbuster and "[" in dirbuster and "]" in dirbuster:
                                dirbuster_one = dirbuster.replace("'", '"')
                                dirbuster_json = json.loads(dirbuster_one)
                                for one in dirbuster_json:
                                    dirbuster_list.append(one)

                '''
                    查询ip对应的域名下的
                '''
                domain_sql ='select domain.dirbuster from online_asset_ip ip,domain_ip_relation dir,online_asset_domain domain where dir.asset_ip_id=ip.id and domain.id=dir.asset_domain_id and ip.ip="%s" and ip.project_id=%d;'%(asset,int(project_id))
                logger.log("domain sql =="+str(domain_sql))
                cursor.execute(domain_sql)
                results = cursor.fetchall()
                logger.log("domain results =="+str(results))
                if results and len(results) >=1:
                    dirbuster_result = results[0]
                    if dirbuster_result:
                        dirbuster_json = json.loads(dirbuster_one)
                        dirbuster_list.append(dirbuster_json)
        except Exception as e:
            logger.log("查询爆破信息出现异常==="+str(e.__str__()))
            raise Exception("查询爆破信息出现异常==="+str(e.__str__()))
        finally:
            if cursor:
                cursor.close()
            return dirbuster_list














