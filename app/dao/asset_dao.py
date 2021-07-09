# -*- coding:UTF-8 -*-
'''
    资产操作
    域名按钮:
   子域名按钮:cdn判断,真实ip判断
   主域名按钮:子域名收集&爆破,cdn判断,域名的whois_info，真实ip判断

ip按钮:
   真实IP:旁站拓展,c段扫描,端口探测,ip位置&出口诊断
   c段IP:端口探测,ip位置&出口诊断

服务按钮:
	非web按钮:banner探测
	web按钮:banner探测,web资产深度识别,web title抓取&截图,ssl证书获取
'''
from django.db import connection
from app.models import OnlineAssetDomain,OnlineSecurity,OnlineAssetIp,DomainIpRelation,MarmoLog,ModuleFunction
from app.utils.marmo_logger import Marmo_Logger
import json
from app.models import MarmoProject
logger =Marmo_Logger()
class AssetDao():

    def get_dict_data(self,data,keyword):
        assert isinstance(data,dict)
        if data.__contains__(keyword):
            result = data[keyword]
            return result or "";
        else:
            return ""
    '''
        查询状态信息
    '''
    def query_asset_module_function_status(self,asset_id,project_id,asset_type):
        functions = ModuleFunction.objects.filter(asset_id=asset_id).filter(asset_type=asset_type).filter(project_id=project_id)[:]
        function_list =""
        if functions:

            for function in functions:
                # function_obj =""
                function_name =function.module_name
                function_status=function.module_status
                temp_status =""
                if function_status ==0:
                    # function_obj["status"]="未开始"
                    temp_status="未开始"
                elif function_status ==1:
                    # function_obj["status"] = "进行中"
                    temp_status="进行中"
                elif function_status ==2:
                    # function_obj["status"] = "已结束"
                    temp_status ="已结束"
                    module_log = function.module_log
                    if module_log:
                        # function_obj["status"]="已结束_有数据"
                        temp_status ="已结束(有数据)"
                    else:
                        temp_status = "已结束(无数据)"
                elif function_status ==3:
                    # function_obj["status"] = "有异常"
                    temp_status ="有异常"
                # function_list.append(function_obj)
                function_list+=function_name+" : "+temp_status+" ; "
        return function_list


    '''
        查询域名资产信息
        input:project_id
        output:data
    '''


    def query_domain(self,data):
        try:
            project_id = data["project_id"]
            page = data["page"] or 1
            limit = data["limit"] or 10
            page_start = (int(page)-1)*int(limit)
            page_end =page_start+int(limit)
            if project_id:
                '''
                    从项目那里进来
                '''
                domain_temp_results = OnlineAssetDomain.objects.filter(project_id=project_id)
            else:
                '''
                    查询全部域名资产项目
                '''
                domain_temp_results = OnlineAssetDomain.objects.all()
            if data["domain"]:
                domain_temp_results =domain_temp_results.filter(domain_name__contains=data["domain"])
            domain_results_count = domain_temp_results.count()
            domain_results = domain_temp_results[page_start:page_end]
            domain_list =[]
            for domain in domain_results:
                domain_obj ={}
                domain_obj["id"]=domain.id
                domain_obj["asset"]=domain.domain_name
                domain_obj["source"]=domain.source
                domain_obj["source_detail"]=domain.source_detail
                domain_obj["description"]=domain.description
                domain_obj["domain_type"]=domain.domain_type
                domain_obj["cdn"]=domain.is_include_cdn_ip
                domain_obj["create_time"]=domain.create_time
                domain_obj["whois_info"]=domain.whois_info
                domain_obj["extra_info"]=domain.extra_info
                project_id = domain.project_id
                '''
                    查询项目名称
                '''
                project_obj = MarmoProject.objects.filter(id=int(project_id)).get()
                domain_obj["project_name"]=project_obj.name
                '''
                    查询资产状态信息
                '''
                function_list = self.query_asset_module_function_status(domain.id,project_id,1)
                domain_obj["function_status"]=function_list
                domain_list.append(domain_obj)
            return domain_list,domain_results_count
        except Exception as e:
            print("query domain 出现异常==="+str(e.__str__()))
            raise Exception("query domain 出现异常==="+str(e.__str__()))

    '''
        修改资产信息
        "domain_name":domain_name,
                "domain_type":domain_type,
                "source": source,
                "is_cdn": is_cdn,
                "whois_info": whois_info,
                "extra_info": extra_info,
                "description": description,
                "domain_id": domain_id,
    '''
    def update_domain_asset(self,data):
        try:
            project_id =""
            if data.__contains__("project_id"):
                project_id = data["project_id"]
            if data.__contains__("project_name"):
                project_name =data["project_name"]
                if project_name:
                    project_obj = self.query_project_exists_by_name(project_name)
                    if project_obj:
                        project_id = project_obj.id
            if project_id:
                domain_asset =OnlineAssetDomain.objects.filter(id=int(data["domain_id"]),project_id=int(project_id)).get()
                if domain_asset:
                    if data.__contains__("domain_name"):
                        domain_asset.domain_name=self.get_dict_data(data,"domain_name")
                    if data.__contains__("source"):
                        domain_asset.source = self.get_dict_data(data,"source")
                    if data.__contains__("domain_type"):
                        domain_asset.domain_type=self.get_dict_data(data,"domain_type")
                    if data.__contains__("is_cdn"):
                        domain_asset.is_include_cdn_ip =self.get_dict_data(data,"is_cdn")
                    if data.__contains__("whois_info"):
                        domain_asset.whois_info =self.get_dict_data(data,"whois_info")
                    if data.__contains__("extra_info"):
                        domain_asset.extra_info = self.get_dict_data(data,"extra_info")
                    if data.__contains__("description"):
                        domain_asset.description =  self.get_dict_data(data,"description")
                    domain_asset.save()
                    return True
                else:
                    raise Exception("更新域名资产不存在")
            else:
                raise  Exception("更新域名参数project_id丢失")
        except Exception as e:
            raise Exception("update_domain_asset 出现异常==="+str(e.__str__()))

    '''
        查询ip
        两种查询方式:
        查项目的ip
        查域名指定的ip
        
    '''
    def query_ip_asset(self,data):
        cursor = connection.cursor()
        try:
            asset =data["domain"]
            ip =data["ip"]
            page = data["page"] or 1
            limit = data["limit"] or 10
            page_start = (int(page) - 1) * int(limit)
            page_end = page_start + int(limit)
            ip_list =[]
            # project_id = data["project_id"]
            select_sql =""
            if asset or ip:
                '''
                    查询关联域名对应的id,这种查询不支持c段IP查询
                '''
                query_ip_type =""
                if ip:
                    '''
                        ip类型可能是C段IP/真实IP,模糊查询c段IP
                    '''
                    ip_type_sql ="select ip_type from online_asset_ip ip where ip.ip='%s'"%(ip)
                    cursor.execute(ip_type_sql)
                    ip_results = cursor.fetchall()
                    if ip_results and len(ip_results) >=1:
                        ip_result = ip_results[0]
                        if len(ip_result) >=1:
                            ip_type = ip_result[0]
                            query_ip_type = ip_type

                if query_ip_type:
                    if ip_type ==1 or ip_type =="1":
                        '''
                            真实IP
                        '''
                        select_sql = "select a.* ,project.name from (select ip.id,ip.ip,ip.source,ip.source_detail,ip.ip_type,domain.domain_name,ip.location,ip.org,ip.create_time,ip.is_belongs_to,ip.extra_info,ip.rdns_history,ip.description,ip.project_id from online_asset_ip ip,domain_ip_relation dir,online_asset_domain domain where ip.id=dir.asset_ip_id and domain.id=dir.asset_domain_id"
                        if asset:
                            select_sql += " and (domain_name like '%" + asset + "%' or ip.source_detail like '%" + asset + "%')"
                        if ip:
                            select_sql += " and ip.ip like '%" + ip + "%'";
                        select_sql += ") a left join marmo_project project on a.project_id=project.id limit %d,%d;" % (
                        page_start, int(limit))
                    elif ip_type ==4 or ip_type =="4":
                        '''
                            c段IP,不用查询domain_ip_relation,域名条件直接是source_detail
                        '''
                        select_sql = "select a.* ,project.name from (select ip.id,ip.ip,ip.source,ip.source_detail,ip.ip_type,ip.source_detail asset,ip.location,ip.org,ip.create_time,ip.is_belongs_to,ip.extra_info,ip.rdns_history,ip.description,ip.project_id from online_asset_ip ip  where 1=1 "
                        if asset:
                            select_sql += " and ip.source_detail like '%"+asset+"%'"
                        if ip:
                            select_sql += " and ip.ip='"+ip+"'";
                        select_sql += ") a left join marmo_project project on a.project_id=project.id limit %d,%d;" % (
                            page_start, int(limit))
                else:
                    '''
                        只通过域名框查询
                    '''
                    select_sql = "select a.* ,project.name from (select ip.id,ip.ip,ip.source,ip.source_detail,ip.ip_type,domain.domain_name,ip.location,ip.org,ip.create_time,ip.is_belongs_to,ip.extra_info,ip.rdns_history,ip.description,ip.project_id from online_asset_ip ip,domain_ip_relation dir,online_asset_domain domain where ip.id=dir.asset_ip_id and domain.id=dir.asset_domain_id "
                    if asset:
                        select_sql += " and (domain_name like '%" + asset + "%' or ip.source_detail like '%" + asset + "%') "
                    select_sql += " ) a left join marmo_project project on a.project_id=project.id limit %d,%d;" % (
                        page_start, int(limit))



            else:
                '''
                    查询全部的ip资产数据
                '''
                select_sql="select a.* ,project.name from (select ip.id,ip.ip,ip.source,ip.source_detail,ip.ip_type,ip.source_detail asset,ip.location,ip.org,ip.create_time,ip.is_belongs_to,ip.extra_info,ip.rdns_history,ip.description,ip.project_id from online_asset_ip ip) a left join marmo_project project on a.project_id=project.id limit %d,%d"%(page_start,int(limit))
            print(select_sql)
            cursor.execute(select_sql)
            results =cursor.fetchall()
            print(results)
            count_sql ="select count(1) from online_asset_ip"
            cursor.execute(count_sql)
            count = int(cursor.fetchone()[0])
            cip_list = []
            for result in results:
                ip_obj ={}
                ip_obj["id"]=result[0]
                ip_obj["ip"]=result[1]
                ip_obj["source"]=result[2]
                ip_obj["source_detail"]=result[3]
                ip_obj["ip_type"]=result[4]
                ip_obj["asset"]=result[5]
                ip_obj["ip_location"]=result[6]
                ip_obj["org"] = result[7]
                ip_obj["create_time"] = result[8]
                ip_obj["is_belongs_to"]=result[9]
                ip_obj["extra_info"]=result[10]
                ip_obj["rdns_history"]=result[11]
                ip_obj["description"]=result[12]
                ip_project_id = result[13]
                ip_obj["project_name"]=result[14]
                '''
                    查询资产状态信息
                '''
                function_list = self.query_asset_module_function_status(int(result[0]), ip_project_id,2)
                ip_obj["function_status"] = function_list
                ip_list.append(ip_obj)
            # for cip in cip_list:
            #     if cip:
            #         '''
            #            查询c段IP
            #         '''
            #         cip_select_sql ='select a.* ,project.name from (select ip.id,ip.ip,ip.source,ip.source_detail,ip.ip_type,domain.domain_name,ip.location,ip.org,ip.create_time,ip.is_belongs_to,ip.extra_info,ip.rdns_history,ip.description,ip.project_id from online_asset_ip ip,online_asset_domain domain where ip.source_detail like "%'+str(cip)+'%") a left join marmo_project project on a.project_id=project.id'
            #         cursor.execute(cip_select_sql)
            #         cip_results =
            return ip_list,count
        except OnlineAssetDomain.DoesNotExist:
            logger.log("域名不存在")
            return [],0
        except Exception as e:
            logger.log("query ip asset 出现异常==="+str(e.__str__()))
            raise Exception("query ip asset 出现异常==="+str(e.__str__()))

    '''
        新增域名
        domain_name:域名值
        project_name:项目名称
        description:
        domain_type:域名类型
        source_detail:来源详情
        description:备注
        
        新增域名的同时建立该域名的模块功能
    '''
    def create_domain(self,data):
        try:
            query_project_by_name = self.query_project_exists_by_name(data["project_name"])
            if query_project_by_name:
                project_id = query_project_by_name.id
                create_domain_obj ={
                    "domain_name":data["domain_name"],
                    "source":data["source"],
                    "project_id":project_id,
                    "description":data["description"],
                    "source_detail":data["source_detail"],
                    "domain_type":int(data["domain_type"]),
                    "is_include_cdn_ip":2,
                }
                domain_type = int(data["domain_type"])
                if data.__contains__("celery_status"):
                    create_domain_obj["celery_status"]=data["celery_status"]
                else:
                    if domain_type ==1:
                        create_domain_obj["celery_status"]="1P"
                    else:
                        create_domain_obj["celery_status"] = "3P"

                '''
                    domain插入前要先去重和全部小写
                '''
                domain_letter =data["domain_name"].lower()
                domain_exists =OnlineAssetDomain.objects.filter(domain_name=domain_letter).exists()
                if not domain_exists:
                    create_domain_obj["domain_name"] =domain_letter
                    domain_obj=OnlineAssetDomain.objects.create(**create_domain_obj)
                    if domain_obj:
                        '''
                            创建域名对应的功能模块
                        '''
                        domain_obj.save()
                        return True
                    else:
                        return False
                else:
                    logger.log("域名已经存在=="+str(data["domain_name"]))
        except Exception as e:
            logger.log("创建域名出现异常==="+str(e.__str__()))
            raise Exception("创建域名出现异常==="+str(e.__str__()))

    '''
        根据项目名称查询项目是否存在
    '''
    def query_project_exists_by_name(self,project_name):
        assert project_name
        try:
            project_obj = MarmoProject.objects.filter(name=project_name).get()
            return project_obj
        except MarmoProject.DoesNotExist:
            logger.log("新增域名项目不存在")
            raise Exception("新增域名项目不存在")
        except Exception as e:
            logger.log("query project exists "+str(e.__str__()))
            raise Exception("query project exists "+str(e.__str__()))


    '''
        修改IP
        判断关联资产是域名还是ip
        必传:
        project_name
    '''
    def update_ip(self,data):
        try:
            ip =""
            ip_type =""
            extra_info =""
            rdns_history=""
            ip_location =""
            org =""
            source =""
            source_detail=""
            description=""
            is_belongs_to=""
            project_id =""
            dirbuster =""
            asset =""
            project_id =""
            if data.__contains__("project_id"):
                project_id = data["project_id"]
            if data.__contains__("project_name"):
                project_name = data["project_name"]
                if project_name:
                    project_obj =self.query_project_exists_by_name(project_name)
                    if project_obj:
                        project_id = project_obj.id
            if data.__contains__("asset"):
                asset =data["asset"] #这个是要修改关联资产的时候传的参数
            if data.__contains__("dirbuster"):
                dirbuster = data["dirbuster"]
            if data.__contains__("source"):
                source=data["source"]
            if data.__contains__("source_detail"):
                source_detail=data["source_detail"]
            if data.__contains__("ip"):
                ip = data["ip"]
            if data.__contains__("asset"):
                asset = data["asset"]
            if data.__contains__("ip_type"):
                ip_type = data["ip_type"]
            if data.__contains__("ip_location"):
                ip_location = data["ip_location"]
            if data.__contains__("org"):
                org = data["org"]
            if data.__contains__("is_belongs_to"):
                is_belongs_to = data["is_belongs_to"]
            if data.__contains__("extra_info"):
                extra_info = data["extra_info"]
            if data.__contains__("rdns_history"):
                rdns_history = data["rdns_history"]
            if data.__contains__("description"):
                description = data["description"]
            ip_obj = OnlineAssetIp.objects.filter(ip=ip,ip_type=ip_type,project_id=project_id).get()
            if ip_obj:

                if ip_type =="4" or ip_type ==4:
                    '''
                        c段ip,关联资产就是修改source_detail
                    '''
                    if asset:
                        ip_obj.source_detail = asset
                elif ip_type ==1 or ip_type=="1":
                    '''
                        修改ip关联的域名资产,查出ip对应的域名资产id,然后修改domain_ip_relation
                    '''
                    ip_id = ip_obj.id
                    project_id = ip_obj.project_id
                    domain_obj = OnlineAssetDomain.objects.filter(domain_name=asset,project_id=project_id).get()
                    if domain_obj:
                        domain_id = domain_obj.id
                        domain_ip_relation = DomainIpRelation.objects.filter(asset_domain_id=domain_id,asset_ip_id=ip_id).get()
                        if domain_ip_relation:
                            domain_ip_relation.asset_domain_id = domain_id
                            domain_ip_relation.save()
                if ip_type:
                    ip_obj.ip_type = ip_type
                if ip_location:
                    ip_obj.ip_location = ip_location
                ip_obj.org = org
                ip_obj.is_belongs_to = is_belongs_to
                ip_obj.extra_info = extra_info
                ip_obj.rdns_history = rdns_history
                ip_obj.description = description
                ip_obj.save()
                return True
        except OnlineAssetDomain.DoesNotExist:
            logger.log("更新IP关联的域名资产不存在")
            raise Exception("更新IP关联的域名资产不存在")
        except DomainIpRelation.DoesNotExist:
            logger.log("更新IP关联的资产关系表不存在")
            raise Exception("更新IP关联的资产关系表不存在")
        except OnlineAssetIp.DoesNotExist:
            logger.log("更新IP不存在")
            raise Exception("更新IP不存在")
        except Exception as e:
            logger.log("更新IP出现异常="+str(e.__str__()))
            raise Exception("更新IP出现异常="+str(e.__str__()))





    '''
        创建IP
        input:domain:关联的域名
          ip:输入的ip值
          related_ip:关联的ip,如果ip_type是4,那么ip的值就是来源详情
          ip_type:1-真实ip,4-c段IP
          source_detail:来源详情
          description:备注
    '''
    def create_ip(self,data):
        try:
            project_name = data["project_name"]
            project_obj =self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                ip=data["ip"]
                if ip:
                    ip = "".join(ip.split())
                logger.log("ip====="+str(ip))
                ip_type = data["ip_type"]
                related_ip =""
                domain =""
                add_asset_ip_params = {
                    "ip_type": int(ip_type),
                    "location": "",
                    "ip": ip,
                    "org": "",
                    "source": data["source"],
                    "is_belongs_to": 1,
                    "project_id": int(project_id)
                }
                if data.__contains__("celery_status"):
                    add_asset_ip_params["celery_status"]=data["celery_status"]
                else:
                    if ip_type =="1" or ip_type ==1:
                        add_asset_ip_params["celery_status"] ="5P" #默认创建的真实ip状态为5P
                    elif ip_type =="4" or ip_type ==4:
                        add_asset_ip_params["celery_status"] = "7P"
                    else:
                        add_asset_ip_params["celery_status"] = "UK"
                if data.__contains__("source_detail"):
                    source_detail=data["source_detail"]
                    add_asset_ip_params["source_detail"]=source_detail
                if data.__contains__("related_ip"):
                    related_ip =data["related_ip"]
                    add_asset_ip_params["source_detail"]=related_ip  #关联ip
                if data.__contains__("description"):
                    description = data["description"]
                    add_asset_ip_params["description"]=description
                if data.__contains__("domain"):
                    domain = data["domain"]
                '''
                    检查ip是否已经存在
                '''
                ip_exists = OnlineAssetIp.objects.filter(ip=ip,project_id=int(project_id)).exists()
                logger.log("ip_exists=="+str(ip_exists))
                logger.log("related_ip==="+str(related_ip))
                logger.log("domain ==="+str(domain))
                if not ip_exists:
                    if ip and related_ip:
                        '''
                            ip绑定IP,查询被绑定的IP是否存在 
                        '''
                        is_ip_exists,ip_query_exists_obj = self.query_ip_exists({
                            "ip":related_ip,
                            "project_id":int(project_id)
                        })
                        if is_ip_exists:
                            ip_obj =OnlineAssetIp.objects.create(**add_asset_ip_params)
                            if ip_obj:
                                return True
                            else:
                                return False
                    elif ip and domain:
                        '''
                            ip绑定域名资产
                        '''
                        logger.log("输入的域名=="+str(domain))
                        add_asset_ip_params["source_detail"]=source_detail
                        is_exists,domain_obj = self.query_domain_exists({
                            "domain":domain,
                            "project_id":int(project_id)
                        })
                        if is_exists:
                            domain_id = domain_obj.id
                            ip_obj = OnlineAssetIp.objects.create(**add_asset_ip_params)
                            if ip_obj:
                                ip_id = ip_obj.id

                                '''
                                    插入domain_ip_relation表记录
                                '''
                                domain_ip_relation =DomainIpRelation(asset_domain_id=domain_id,asset_ip_id=ip_id)
                                domain_ip_relation.save()
                                ip_obj.save()
                                return True
                            else:
                                raise Exception("创建IP记录失败")
                        else:
                            raise Exception("输入的域名不存在")
                    else:
                        '''
                            程序里面添加的，没有关联域名和ip,要根据ip查询域名
                        '''
                        logger.log("ip没有关联域名和ip,异常")
                else:
                    logger.log("ip已经存在，不能重复添加相同的ip数据")
                    return False

        except Exception as e:
            logger.log("创建ip出现异常==="+str(e.__str__()))
            raise Exception("创建ip出现异常==="+str(e.__str__()))
    '''
        创建安全设备表
        security_name:
        company:
        project_name:
        source_detail:
        description:
        
    '''
    def create_security(self,data):
        try:
            project_name = data["project_name"]
            query_project_by_name = self.query_project_exists_by_name(project_name)
            if query_project_by_name:
                project_id = query_project_by_name.id
                create_security_obj ={
                    "security_name":data["security_name"],
                    "source":2,
                    "company":data["company"],
                    "source_detail":data["source_detail"],
                    "description":data["description"],
                    "project_id":project_id
                }
                security_obj=OnlineSecurity.objects.create(**create_security_obj)
                if security_obj:
                    return True
                else:
                    return False
            else:
                raise Exception("创建安全设备项目不存在")
        except Exception as e:
            logger.log("创建安全设备出现异常==="+str(e.__str__()))
            raise Exception("创建安全设备出现异常==="+str(e.__str__()))

    '''
        修改安全设备
    '''
    def update_security(self,data):
        try:
            update_security_obj ={
                "security_name":data["security_name"],
                "source":data["source"],
                "company":data["company"],
                "source_detail":data["source_detail"],
                "description":data["description"]

            }
            security_obj=OnlineSecurity.objects.filter(security_name=data["security_name"],company=data["company"]).get()
            if security_obj:
                security_obj.source =update_security_obj["source"]
                security_obj.company = update_security_obj["company"]
                security_obj.security_name=update_security_obj["security_name"]
                security_obj.source_detail=update_security_obj["source_detail"]
                security_obj.description =update_security_obj["description"]
                security_obj.save()
                return True
            else:
                raise Exception("修改安全设备不存在")
        except OnlineSecurity.DoesNotExist:
            raise Exception("修改安全设备不存在")
        except Exception as e:
            logger.log("修改安全设备不存在==="+str(e.__str__()))
            raise Exception("修改安全设备不存在==="+str(e.__str__()))

    '''
        查询安全设备
    '''
    def query_security(self,data):
        try:
            security_list =[]
            page = data["page"] or 1
            limit = data["limit"] or 10
            page_start = (int(page) - 1) * int(limit)
            page_end = page_start + int(limit)
            project_id = data["project_id"]
            if project_id:
                security_temp_results = OnlineSecurity.objects.filter(project_id=int(data["project_id"]))
            else:
                security_temp_results = OnlineSecurity.objects.all()
            count = security_temp_results.count()
            security_results = security_temp_results[page_start:page_end]
            if security_results:
                for security in security_results:
                    security_obj ={}
                    security_obj["id"]=security.id
                    security_obj["security_name"]=security.security_name
                    security_obj["source"]=security.source
                    security_obj["company"]=security.company
                    security_obj["create_time"]=security.create_time
                    security_obj["source_detail"]=security.source_detail
                    security_obj["description"]=security.description
                    security_list.append(security_obj)

            return security_list,count
        except Exception as e:
            raise Exception("查询安全设备出现异常=="+str(e.__str__()))


    '''
        查询loginfo，表是module_function
        project_id:项目id
        asset_id:资源id
        asset_type:类型,domain是1，ip是2，service是3，component是4
    '''
    def query_log_info(self,data):
        try:
            # project_name = data["project_name"]
            # project_obj =self.query_project_exists_by_name(project_name)

            # if project_obj:
            #     project_id = project_obj.id
            module_function_result = MarmoLog.objects.filter(type=int(data["asset_type"]),asset_id=int(data["asset_id"]))[:]
            module_log_list = []
            if module_function_result:

                for module_function in module_function_result:
                    log_info = ""
                    module_name=module_function.module
                    module_log =module_function.module_log
                    start_log=("*********"*5)+str(module_name)+" start "+str("****"*5)
                    log_info+=start_log
                    log_info+=("-----------"*10)
                    log_info+=str(module_log)
                    end_log =("*********"*5)+str(module_name)+" end "+str("****"*5)
                    log_info+=end_log
                    module_log_list.append(log_info)


            return module_log_list
        except Exception as e:
            raise Exception("查询log_info出现异常==="+str(e.__str__()))


    '''
        查询所有的域名
        input:project_id
        output:domain_list
    '''
    def query_domain_list(self,data):
        try:
            project_id = int(data["project_id"])
            domain_results = OnlineAssetDomain.objects.filter(project_id=project_id)[:]
            domain_list = []
            for domain in domain_results:
                domain_obj ={}
                domain_obj["id"]=domain.id
                domain_obj["domain_name"]=domain.domain_name
                domain_list.append(domain_obj)
            return domain_list
        except Exception as e:
            raise Exception("查询域名列表出现异常"+str(e.__str__()))


    '''
        查询输入的ip是否正确
        output:True/False,object
    '''
    def query_ip_exists(self,data):
        try:
            ip = data["ip"]
            project_id = data["project_id"]
            online_ip = OnlineAssetIp.objects.filter(ip=ip,project_id=int(project_id)).get()
            if online_ip:
                return True,online_ip
        except OnlineAssetIp.DoesNotExist:
            logger.log("ip不存在")
            return False
        except Exception as e:
            logger.log("query ip exists 出现异常=="+str(e.__str__()))
            raise Exception("query ip exists 出现异常=="+str(e.__str__()))

    '''
        查询输入的域名是否存在
        output:True/False,object
    '''
    def query_domain_exists(self,data):
        try:
            domain = data["domain"]
            project_id = data["project_id"]
            online_domain = OnlineAssetDomain.objects.filter(domain_name=domain,project_id=int(project_id)).get()
            if online_domain:
                return True,online_domain
        except OnlineAssetDomain.DoesNotExist:
            logger.log("域名不存在")
            return False,None
        except Exception as e:
            logger.log("query domain exists 出现异常=="+str(e.__str__()))
            raise Exception("query domain exists 出现异常=="+str(e.__str__()))

    '''
            更新域名表的dirbuster字段,形式是追加
        '''

    def update_domain_dirbuster(self, data):
        try:
            project_name = data["project_name"]
            project_obj = self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                domain = data["domain"]
                asset_id = data["asset_id"]
                dirbuster = data["dirbuster"]
                if domain and project_id and asset_id:
                    onlineassetdomain = OnlineAssetDomain.objects.filter(domain_name=domain, project_id=int(project_id)).get()
                    temp_dirbuster = onlineassetdomain.dirbuster
                    if temp_dirbuster:
                        onlineassetdomain.dirbuster = temp_dirbuster+"#@#"+json.dumps(dirbuster)
                    else:
                        onlineassetdomain.dirbuster = temp_dirbuster + "#@#" + json.dumps(dirbuster)
                    onlineassetdomain.save()
                else:
                    raise Exception("更新域名资产位置信息异常")
        except Exception as e:
            raise Exception("更新域名资产位置信息异常==" + str(e.__str__()))
































