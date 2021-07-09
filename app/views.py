from django.shortcuts import render,redirect,reverse
from django.views import View
from django.http.response import JsonResponse
from app.dao.marmo_dao import UserDao,BaseSettingsDao,ProjectDao
from app.dao import asset_dao
from app.dao import service_dao
from app.dao import vuln_dao
from app.dao import web_recongnize
from app.dao import process_info_dao
from app.dao.sidestations_dao import SideStaionsDao
from datetime import datetime as ddt
import datetime as dt
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout  # 退出session
from base64 import b64encode
from hashlib import md5
from django.db import connection
from django.http import HttpResponseRedirect
from marmo.settings import LOGIN_URL
from app.worker import domain_scheduler,domain_worker_schduler,ip_scheduler,ip_worker_schduler,service_scheduler,service_worker_schduler

class IndexView(View):
    @staticmethod
    def get(request):
        homepage =[{"name":"首页"}]
        path =request.scheme + "://" + request.get_host()
        left_menu = BaseSettingsDao().query_menu()
        user_id = request.session["user_id"]
        user = UserDao().query_user(user_id)
        return render(request,"index.html",{
            "homepage":homepage,"path":path,"leftmenu":left_menu,"user":user
        })


class MenuJson(View):
    @staticmethod
    def get(request):
        '''
            查询个人中心配置
        :return: {code:"",msg:"",data:""}
        '''
        menu = BaseSettingsDao.query_user_center()
        return JsonResponse({"code":"0","msg":"ok","data":menu})

class ProjectView(View):
    @staticmethod
    def get(request):
        request_type = request.GET.get("type")
        if request_type =="html":
            return render(request,"project.html")
        elif request_type == "json":
            project_list,count = ProjectDao().query_all_project()
            return JsonResponse({"code":"0","msg":"ok","data":project_list,"count":count})

    '''
        创建/修改项目
        项目json
       data:{"name":project_name,"customer":customer,"info_group":info_group,"tool_group":tool_group,"expert_group":expert_group,"work_time":work_time,"pentest_tech":pentest_tech,
       "delivery_date":delivery_date,"actual_delivery_date":actual_delivery_date,"summary":summary,"status":project_status,"mode":current_mode}
    '''
    @staticmethod
    def post(request):
        try:
            if request.method =="POST":
                name = request.POST.get("name")
                customer = request.POST.get("customer")
                info_user_id = request.POST.get("info_user_id")
                tool_user_id = request.POST.get("tool_user_id")
                expert_user_id = request.POST.get("expert_user_id")
                work_time = request.POST.get("work_time")
                pentest_tech = request.POST.get("pentest_tech")
                actual_delivery_date = request.POST.get("actual_delivery_date")
                delivery_date = request.POST.get("delivery_date")
                summary = request.POST.get("summary")
                status = request.POST.get("status") or 0
                mode = request.POST.get("mode")
                create_time = ddt.now()
                update_time =ddt.now()
                project_data ={
                    "name":name,
                    "customer":customer,
                    "info_user_id":info_user_id,
                    "tool_user_id":tool_user_id,
                    "expert_user_id":expert_user_id,
                    "work_time":work_time,
                    "pentest_tech":pentest_tech,
                    "actual_delivery_date":actual_delivery_date,
                    "delivery_date":delivery_date,
                    "summary":summary,
                    "status":status,
                    "create_time":create_time,
                    "update_time":update_time
                }
                print(project_data)
                if mode =="create_project":
                    create_result = ProjectDao().create_project(project_data)
                    if create_result:
                        return JsonResponse({"code":"0","msg":"创建项目成功"})
                    else:
                        return JsonResponse({"code": "-1", "msg": "创建项目失败"})
                elif mode =="modify_project":
                    modify_result = ProjectDao().update_marmo_project(project_data)
                    if modify_result:
                        return JsonResponse({"code": "0", "msg": "修改项目成功"})
                    else:
                        return JsonResponse({"code": "-1", "msg": "修改项目失败"})
        except Exception as e:
            print("项目创建/修改失败")
            raise Exception("项目创建/修改失败")

class UserView(View):
    @staticmethod
    def get(request):
        request_type = request.GET.get("type")
        if request_type =="html":
            return render(request,"user.html")
        elif request_type =="json":
            '''
                查询用户的渗透任务
            '''
            user_id = request.GET.get("user_id")
            page = request.GET.get("page")
            process_info_list,count = UserDao().query_user_process_info(user_id,page)
            print(process_info_list,count)
            return JsonResponse({"code":"0","msg":"ok","count":count,"data":process_info_list})
        elif request_type =="user":
            user_list = UserDao().query_all_user()
            return JsonResponse({"code":"0","msg":"ok","data":user_list})

    '''
        修改用户渗透信息状态,任务流转变更，任务状态变更
        {"data":{"type":"translate/change","sender":"","recevier":""}}
        data:{"info_type":info_type,"info_user":info_user,"info_project":info_project,"info_status":info_status,"info_content":info_content,"process_info_id":process_info_id},

    '''
    @staticmethod
    def post(request):
        try:
            info_type = request.POST.get("info_type")
            info_user = request.POST.get("info_user")
            info_project=request.POST.get("info_project")
            info_content=request.POST.get("info_content")
            info_status = request.POST.get("info_status")
            process_info_id = request.POST.get("process_info_id")
            modify_process_info = UserDao().update_process_info({"info_type":info_type,"info_user":info_user,"info_project":info_project,"info_status":info_status,"info_content":info_content,"process_info_id":process_info_id})
            if modify_process_info:
                return JsonResponse({"code":"0","msg":"ok"})
            else:
                return JsonResponse({"code": "-1", "msg": "ok"})
        except Exception as e:
            print("修改渗透任务出现异常==="+str(e.__str__()))
            return JsonResponse({"code": "-1", "msg": "ok"})



class AssetView(View):
    @staticmethod
    def get(request):
        request_type = request.GET.get("type")
        page = request.GET.get("page") or 1
        limit = request.GET.get("limit") or 10
        if request_type =="html":
            project_name = request.GET.get("project_name") or ""
            project_id = request.GET.get("project_id") or ""
            return render(request,"asset_manager.html",{"project_name":project_name,"project_id":project_id})
        elif request_type =="json":
            asset_type = request.GET.get("asset_type")
            project_id = request.GET.get("project_id")

            if asset_type =="domain":
                '''
                    查询域名资产
                '''
                domain = request.GET.get("domain") or ""
                domain_query_data ={"project_id":project_id,"domain":domain,"page":page,"limit":limit}
                domain_list,count = asset_dao.AssetDao().query_domain(domain_query_data)
                return JsonResponse({
                    "code":"0",
                    "msg":"ok",
                    "data":domain_list,
                    "count":count
                })
            elif asset_type =="ip":
                '''
                    查询ip资产
                '''
                ip = request.GET.get("ip")
                domain = request.GET.get("domain")

                ip_query_data = {"project_id": project_id, "domain": domain, "page": page, "limit": limit,"ip":ip}
                ip_list,count = asset_dao.AssetDao().query_ip_asset(ip_query_data)
                print(str(ip_list))
                return JsonResponse({
                    "code": "0",
                    "msg": "ok",
                    "data": ip_list,
                    "count": count
                })

            elif asset_type =="security":
                '''
                    查询安全设备
                '''
                security_query_data = {"project_id": project_id, "page": page, "limit": limit}
                security_list,count = asset_dao.AssetDao().query_security(security_query_data)
                return JsonResponse({
                    "code": "0",
                    "msg": "ok",
                    "data": security_list,
                    "count": count
                })


    '''
        post请求
    '''
    @staticmethod
    def post(request):
        pass

class VulnView(View):

    def get(self,request):
        try:
            type = request.GET.get("type")
            path = request.scheme + "://" + request.get_host()
            if type == "html":
                project_name = request.GET.get("project_name") or ""
                asset = request.GET.get("asset") or ""
                asset_type = request.GET.get("asset_type") or ""
                if project_name and asset:
                    return render(request, "vuln_info.html",
                                  {"project_name": project_name, "path": path, "asset": asset,"asset_type":asset_type})
                else:
                    '''
                        查询全部项目的漏洞
                    '''
                    return render(request, "vuln_info.html",
                                  {"project_name": "", "path": path, "asset": "",
                                   "asset_type": ""})
            elif type == "json":
                user_id = request.GET.get("user_id") or ""
                project_name = request.GET.get("project_name") or None
                asset = request.GET.get("asset") or ""
                asset_type = request.GET.get("asset_type") or ""
                limit = request.GET.get("limit")
                page = request.GET.get("page")
                query_vuln_info_params = {
                    "user_id": user_id,
                    "page": page,
                    "limit": limit,
                    "asset": asset,
                    "asset_type":asset_type
                }
                if project_name:
                    query_vuln_info_params["project_name"]=project_name
                process_info_list, count = vuln_dao.VulnInfoDao().query_vlun_info(query_vuln_info_params)
                return JsonResponse({
                    "code": "0",
                    "msg": "ok",
                    "count": count,
                    "data": process_info_list
                })
        except Exception as e:
            print("查询漏洞信息出现异常==" + str(e.__str__()))


    def post(self,request):
        try:
            '''
               asset:asset,
                asset_type:asset_type,
                project_name:project_name,
                vuln_name:vuln_name,
                vuln_level:vuln_level,
                vuln_affect:vuln_affect,
                vuln_details:vuln_details,
                request_type:"add",
                user_id:user_id
            '''
            request_type = request.POST.get("request_type")
            if request_type == "add":
                asset = request.POST.get("asset")
                asset_type = request.POST.get("asset_type")
                project_name=request.POST.get("project_name")
                vuln_name = request.POST.get("vuln_name")
                vuln_level = request.POST.get("vuln_level")
                vuln_affect = request.POST.get("vuln_affect")
                vuln_details = request.POST.get("vuln_details")
                user_id =request.POST.get("user_id")
                add_vuln_info = {
                    "asset":asset,
                    "asset_type": asset_type,
                    "vuln_name": vuln_name,
                    "vuln_level": vuln_level,
                    "vuln_affect": vuln_affect,
                    "vuln_details": vuln_details,
                    "project_name":project_name,
                    "user_id":user_id
                }
                add_vuln = vuln_dao.VulnInfoDao().create_vuln_info(add_vuln_info)
                if add_vuln:
                    return JsonResponse({
                        "code": "0",
                        "msg": "新增漏洞成功"
                    })
                else:
                    raise Exception("新增漏洞失败")
            elif request_type =="modify":
                vuln_name = request.POST.get("vuln_name")
                vuln_level = request.POST.get("vuln_level")
                vuln_affect = request.POST.get("vuln_affect")
                vuln_details = request.POST.get("vuln_details")
                vuln_status = request.POST.get("vuln_status")
                is_retest = request.POST.get("is_retest")
                vuln_desc = request.POST.get("vuln_desc")
                project_name = request.POST.get("project_name")
                update_vuln_params = {
                    "vuln_name": vuln_name,
                    "vuln_level": vuln_level,
                    "vuln_affect": vuln_affect,
                    "vuln_details": vuln_details,
                    "vuln_status": vuln_status,
                    "is_retest": is_retest,
                    "vuln_desc": vuln_desc,
                    "project_name": project_name
                }
                update_results = vuln_dao.VulnInfoDao().update_vuln_info(update_vuln_params)
                if update_results:
                    return JsonResponse({
                        "code": "0",
                        "msg": "修改漏洞成功"
                    })
                else:
                    raise Exception("修改漏洞失败")
        except Exception as e:
            print("新增/修改漏洞失败" + str(e.__str__()));
            return JsonResponse({
                "code": "-1",
                "msg": "新增/修改漏洞失败" + str(e.__str__())
            })

class ProcessInfoView(View):

    def get(self,request):
        try:
            type = request.GET.get("type")
            path = request.scheme + "://" + request.get_host()
            print(path)
            if type =="html":
                project_name = request.GET.get("project_name") or ""
                asset = request.GET.get("asset") or ""
                if project_name and asset:
                    return  render(request,"process_info.html",{"project_name":project_name,"path":path,"asset":asset})
                else:
                    raise Exception("查询渗透任务参数不正确")
            elif type =="json":
                user_id = request.GET.get("user_id") or ""
                project_name = request.GET.get("project_name")
                asset = request.GET.get("asset") or ""
                limit = request.GET.get("limit")
                page = request.GET.get("page")
                query_process_info_params ={
                    "user_id":user_id,
                    "project_name":project_name,
                    "page":page,
                    "limit":limit,
                    "asset":asset
                }
                process_info_list,count = process_info_dao.ProcessInfoDao().query_process_info(query_process_info_params)
                return JsonResponse({
                    "code":"0",
                    "msg":"ok",
                    "count":count,
                    "data":process_info_list
                })
        except Exception as e:
            print("查询渗透任务出现异常=="+str(e.__str__()))





    def post(self,request):
        try:
            '''
                    asset:asset,
                    asset_type:asset_type,
                    info_content:info_content,
                    info_level:info_level,
                    responser:responser,
                    user_id:user_id
            :param request:
            :return:
            '''

            request_type =request.POST.get("request_type")
            if request_type =="add":
                asset = request.POST.get("asset")
                project_name = request.POST.get("project_name")
                info_content = request.POST.get("info_content")
                info_level = request.POST.get("info_level")
                responser = request.POST.get("responser")
                user_id = request.POST.get("user_id")
                add_prcess_info = {
                    "asset":asset,
                    "project_name":project_name,
                    "info_content":info_content,
                    "info_level":info_level,
                    "responser":responser,
                    "user_id":user_id
                }
                add_process = process_info_dao.ProcessInfoDao().create_process_info(add_prcess_info)
                if add_process:
                    return JsonResponse({
                        "code":"0",
                        "msg":"新增渗透信息成功"
                    })
                else:
                    raise Exception("新增渗透信息失败")
            elif request_type =="modify":
                '''
                    user_id:user_id,
                  project_name:project_name,
                  prcess_info_id:process_info_id,
                  process_user:process_user,
                  info_status:info_status,
                  info_content:info_content,
                  request_type:"modify"
                '''
                user_id = request.POST.get("user_id")
                project_name = request.POST.get("project_name")
                prcess_info_id = request.POST.get("prcess_info_id")
                process_user = request.POST.get("process_user")
                info_status = request.POST.get("info_status")
                info_content = request.POST.get("info_content")
                update_process_params ={
                    "user_id":user_id,
                    "project_name":project_name,
                    "process_info_id": prcess_info_id,
                    "info_user": process_user,
                    "info_status": info_status,
                    "info_content": info_content,

                }
                update_results = process_info_dao.ProcessInfoDao().update_process_info(update_process_params)
                if update_results:
                    return JsonResponse({
                        "code":"0",
                        "msg":"修改渗透任务成功"
                    })
                else:
                    raise Exception("修改渗透任务失败")
        except Exception as e:
            print("新增/修改渗透信息失败"+str(e.__str__()));
            return JsonResponse({
                "code": "-1",
                "msg": "新增/修改渗透信息失败"+str(e.__str__())
            })


'''
    端口view
'''
class ServiceView(View):
    @staticmethod
    def get(request):
        request_type = request.GET.get("request_type") or ""
        page_type = request.GET.get("type") or ""  #web  not_web
        project_name = request.GET.get("project_name")
        asset = request.GET.get("asset")
        page = request.GET.get("page")
        limit =request.GET.get("limit")
        query_data = {
            "project_name": project_name,
            "asset":asset,
            "page":page,
            "limit":limit
        }
        if request_type =="html":
            '''
                页面
            '''
            return render(request, "services.html", {"project_name": project_name, "asset": asset})
        elif request_type =="json":
            if project_name:
                if page_type == "not_web": #非web资产查询
                    # port = request.GET.get("port") or ""  #端口号
                    # service_name = request.GET.get("service_name") #banner
                    # if port:
                    #     query_data["port"]=int(port)
                    # if service_name:
                    #     query_data["service_name"]=service_name
                    service_list,count =service_dao.ServiceDao().query_not_web_service(query_data)
                    return JsonResponse({"code":"0","msg":"ok","data":service_list,"count":count})
                elif page_type =="web": #web资产查询
                    # port = request.GET.get("port") or ""
                    # module_name = request.GET.get("module_name") or ""
                    # module_version = request.GET.get("module_version") or ""
                    # if port:
                    #     query_data["port"] = int(port)
                    # if module_name:
                    #     query_data["module_name"] = module_name
                    # if module_version:
                    #     query_data["version"]=module_version
                    not_web_service_list = service_dao.ServiceDao().query_web_service(query_data)
                    return JsonResponse({"code": "0", "msg": "ok", "data": not_web_service_list})


    @staticmethod
    def post(request):
        try:
            request_type = request.POST.get("type")
            web_type = request.POST.get("web_type")
            if request_type =="add":
                '''
                    新增端口,有web端口，非web端口
                    参数:port,asset,source自动改成人工1,srv_type,project_id
                '''
                port = request.POST.get("port")
                asset = request.POST.get("asset")
                project_name = request.POST.get("project_name")
                description=request.POST.get("description")
                source_detail = request.POST.get("source_detail")
                web_type =request.POST.get("web_type")
                if port and asset and project_name:
                    service_add_data = {
                        "port": port,
                        "asset": asset,
                        "project_name": project_name,
                        "source": 1,
                        "description": description,
                        "source_detail":source_detail,
                        "web_type":web_type
                    }
                    if web_type =="not_web":
                        '''
                            非web端口添加
                        '''
                        service_add_data["srv_type"]=9
                    elif web_type == "web":
                        '''
                            web端口添加
                        '''
                        service_add_data["srv_type"]=1
                    service_add_results = service_dao.ServiceDao().create_service(service_add_data)
                    if service_add_results:
                        return JsonResponse({"code":"0","msg":"ok"})
                    else:
                        raise Exception("新增web端口失败")

                else:
                    raise Exception("新增web端口参数缺少")
            elif request_type =="modify":
                '''
                    修改端口服务信息
                '''
                port = request.POST.get("port")
                source = request.POST.get("source")
                asset = request.POST.get("asset_ip")
                banner = request.POST.get("banner")
                is_deep_http_recongnize = request.POST.get("is_deep_recongnize")
                description = request.POST.get("description")
                asset_id = request.POST.get("asset_id")
                if web_type =="not_web":
                    '''
                        web端口信息修改
                    '''

                    update_not_web_params ={
                        "port":port,
                        "source":int(source),
                        "asset":asset,
                        "banner":banner,
                        "is_deep_http_recongnize":int(is_deep_http_recongnize),
                        "description":description,
                        "asset_id":asset_id
                    }
                    update_result =service_dao.ServiceDao().update_not_web_service(update_not_web_params)
                    if update_result:
                        return JsonResponse({"code": "0", "msg": "ok"})
                    else:
                        raise Exception("修改端口信息异常="+str(update_result))
                elif web_type =="web":
                    #web资产更新功能
                    http_ssl_version = request.POST.get("ssl_version")

                    http_resp_body = request.POST.get("response")
                    http_resp_header = request.POST.get("header")
                    screenshot = request.POST.get("screenshot")



        except Exception as e:
            print("service view 出现异常=="+str(e.__str__()))
            return JsonResponse({"code":"-1","msg":"service view 出现异常=="+str(e.__str__())});


class DomainView(View):
    '''
        方法有修改和新增
    '''
    def post(self,request):
        try:
            request_type = request.POST.get("request_type")
            if request_type =="add":
                '''
                    域名新增
                    "domain_name":domain_name,
                "domain_type":domain_type,
                "project_name":project_name,
                "source_detail":source_detail,
                "description":description,
                "user_id":user_id,     
                '''
                domain_name = request.POST.get("domain_name")
                domain_type = request.POST.get("domain_type")
                project_name = request.POST.get("project_name")
                source_detail = request.POST.get("source_detail")
                description = request.POST.get("description")
                add_domain_params ={
                    "domain_name":domain_name,
                    "domain_type":int(domain_type),
                    "project_name":project_name,
                    "source_detail":source_detail,
                    "description":description,
                    "source":2,
                }
                if domain_type =="1" or domain_type ==1:
                    add_domain_params["celery_status"]="1P"
                elif domain_type =="2" or domain_type ==2:
                    add_domain_params["celery_status"] = "1P"
                create_domain_result =asset_dao.AssetDao().create_domain(add_domain_params)
                if create_domain_result:
                    return JsonResponse({"code":"0","msg":"ok"})
                else:
                    raise Exception("创建域名出现异常")

            elif request_type =="modify":
                '''
                    域名修改
                    "request_type":"update",
                    "domain_name":domain_name,
                    "domain_type":domain_type,
                    "source":source,
                    "is_cdn":is_cdn,
                    "whois_info":whois_info,
                    "extra_info":extra_info,
                    "description":description
                '''
                domain_name = request.POST.get("domain_name")
                domain_type = request.POST.get("domain_type")
                source = request.POST.get("source")
                is_cdn = request.POST.get("is_cdn")
                whois_info = request.POST.get("whois_info")
                extra_info = request.POST.get("extra_info")
                description = request.POST.get("description")
                domain_id = request.POST.get("domain_id")
                project_name = request.POST.get("project_name") or ""

                update_domain_params ={
                    "domain_name":domain_name,
                    "domain_type":domain_type,
                    "source": source,
                    "is_cdn": is_cdn,
                    "whois_info": whois_info,
                    "extra_info": extra_info,
                    "description": description,
                    "domain_id": domain_id,
                }
                if project_name:
                    update_domain_params["project_name"]=project_name
                print(update_domain_params)
                update_domain_result = asset_dao.AssetDao().update_domain_asset(update_domain_params)
                if update_domain_result:
                    return JsonResponse({"code": "0", "msg": "修改域名成功"})
                else:
                    raise Exception("修改域名出现异常")
        except Exception as e:
            print("域名出现异常=="+str(e.__str__()))
            return JsonResponse({"code": "-1", "msg": "新增/修改域名出现异常"+str(e.__str__())})





class IPView(View):
    '''
        方法有修改和新增
    '''

    def post(self, request):
        try:
            request_type = request.POST.get("request_type")
            if request_type == "add":
                '''
                    ip新增
                    ip=data["ip"]
                project_id=data["project_id"]
                description=data["description"]
                domain=data["domain"]
                ip_type=data["ip_type"]
                source_detail=data["source_detail"]
                related_ip =data["related_ip"]
                '''
                ip = request.POST.get("ip")
                domain = request.POST.get("domain") or ""
                related_ip = request.POST.get("related_ip") or ""
                source_detail = request.POST.get("source_detail")
                ip_type = request.POST.get("ip_type")
                description = request.POST.get("description")
                project_name = request.POST.get("project_name")
                add_ip_params ={
                    "ip":ip,
                    "domain":domain,
                    "related_ip":related_ip,
                    "source_detail":source_detail,
                    "ip_type":ip_type,
                    "description":description,
                    "project_name":project_name,
                    "source":2
                }
                add_ip_results = asset_dao.AssetDao().create_ip(add_ip_params)
                if add_ip_results:
                    return JsonResponse({
                        "code":"0",
                        "msg":"新增ip成功"
                    })
                else:
                    raise Exception("新增ip失败")
            elif request_type == "modify":
                '''
                ip修改
                "ip":ip,
                  "asset":asset,
                  "ip_type":ip_type,
                  "ip_location":ip_location,
                  "org":org,
                  "is_belongs_to":is_belongs_to,
                  "extra_info":extra_info,
                  "rdns_history":rdns_history,
                  "description":description
                '''
                ip = request.POST.get("ip")
                asset = request.POST.get("asset")
                ip_type = request.POST.get("ip_type")
                ip_location = request.POST.get("ip_location")
                org = request.POST.get("org")
                is_belongs_to = request.POST.get("is_belongs_to")
                extra_info = request.POST.get("extra_info")
                rdns_history = request.POST.get("rdns_history")
                description = request.POST.get("description")
                project_name = request.POST.get("project_name")
                update_ip_params ={
                    "ip":ip,
                    "asset":asset,
                    "ip_type":ip_type,
                    "ip_location":ip_location,
                    "org":org,
                    "is_belongs_to":is_belongs_to,
                    "extra_info":extra_info,
                    "rdns_history":rdns_history,
                    "description":description,
                    "project_name":project_name
                }
                update_ip_result = asset_dao.AssetDao().update_ip(update_ip_params)
                if update_ip_result:
                    return JsonResponse({
                        "code":"0",
                        "msg":"修改ip成功"
                    })
                else:
                    raise Exception("修改ip失败")

        except Exception as e:
            print("新增/修改ip出现异常=="+str(e.__str__()))
            return JsonResponse({
                "code":"-1",
                "msg":"新增/修改ip出现异常=="+str(e.__str__())
            })


class SecurityView(View):
    def get(self,request):
        pass

    def post(self,request):
        try:
            request_type = request.POST.get("request_type")
            security_name = request.POST.get("security_name")
            company = request.POST.get("company")
            source_detail = request.POST.get("source_detail")
            description = request.POST.get("description")
            security_params ={
                "security_name":security_name,
                "company":company,
                "source_detail":source_detail,
                "description":description
            }
            '''
                "security_name":security_name,
                "company":company,
                "project_name":project_name,
                "source_detail":source_detail,
                "description":description,
                "request_type":"add"
            '''
            if request_type == "add":
                '''
                    安全设备新增
                '''
                project_name = request.POST.get("project_name")
                security_params["project_name"]=project_name
                add_security = asset_dao.AssetDao().create_security(security_params)
                if add_security:
                    return JsonResponse({
                        "code":"0",
                        "msg":"新增安全设备成功"
                    })
            elif request_type == "modify":
                '''
                安全设备修改
                '''
                source = request.POST.get("source")
                security_params["source"]=source
                update_security = asset_dao.AssetDao().update_security(security_params)
                if update_security:
                    return JsonResponse({
                        "code": "0",
                        "msg": "修改安全设备成功"
                    })
        except Exception as e:
            print("新增/修改安全设备出现异常"+str(e.__str__()))
            return JsonResponse({
                "code": "-1",
                "msg": "新增/修改安全设备出现异常"+str(e.__str__())
            })




class LoginView(View):
    def make_cookie(self, username, userpass):
        now = ddt.now()
        six_hour_timestamp = int((now + dt.timedelta(hours=6)).timestamp())
        finally_result = "username=" + str(username) + "&salt=derui@321" + "&password=" + str(
            userpass) + "&expires=" + str(six_hour_timestamp)
        return b64encode(finally_result.encode("utf-8")).decode("utf-8")
    # 登陆
    def get(self,request):
        print("login view")
        path = request.scheme + "://" + request.get_host()
        type = request.GET.get("login_type")
        if type =="verify_account":
            self.verify_account(request)
        elif type =="quit":
            self.quit(request)
        else:
            return render(request,"login.html",{'path': path})

    def post(self,request):
        return self.login(request)

    def login(self,request):
            username = request.POST.get("username")  # 获取前台post 提交的username
            password = request.POST.get("password")  # 获取前台post 提交的password
            print(username, password)
            user_pass = md5(password.encode("utf-8")).hexdigest()

            user = UserDao().get_user(account=username,password=user_pass)
            request.session.set_expiry(10000)
            response = redirect('/index/')
            token =self.make_cookie(username,user_pass)
            response.set_cookie('token', token,expires=60*60*6)
            request.session['user_id'] = user.id  # 给session放入userid字段(uuid)需要转str之后再替换
            request.session['nickname'] = user.nickname  # 给session放入user_full_name字段
            request.session["token"]=token
            return response

    # 退出方法
    @csrf_protect
    def quit(self,request):
        user_id = request.session.get('user_id')
        # Online.objects.filter(user_id=user_id).delete()  # 删除当前用户上线记录
        logout(request)
        return redirect('/index')

class LogInfoView(View):
    def get(self,request):
        try:
            '''
                asset_type=domain
                asset
                project_name
            :return:
            '''
            asset_type =request.GET.get("asset_type")
            asset_id = request.GET.get("asset_id")
            project_name = request.GET.get("project_name")
            query_log_params ={
                "asset_type":asset_type,
                "asset_id":asset_id,
                "project_name":project_name
            }
            loginfo = asset_dao.AssetDao().query_log_info(query_log_params)
            return JsonResponse({
                "code":"0",
                "msg":"ok",
                "info":loginfo
            })
        except Exception as e:
            print("查询loginfo出现异常=="+str(e.__str__()))
            return JsonResponse({
                "code": "-1",
                "msg": "ok",
                "info": "查询loginfo出现异常=="+str(e.__str__())
            })



class WebrecongnizeView(View):
    def get(self,request):
        try:
            request_type = request.GET.get("type")
            project_name = request.GET.get("project_name")
            asset = request.GET.get("asset")
            page = request.GET.get("page")
            limit = request.GET.get("limit")
            path =request.scheme + "://" + request.get_host()
            if request_type =="html":
                return render(request,"web_recongnize.html",{"project_name":project_name,"asset":asset,"path":path})
            elif request_type =="json":
                component_name = request.GET.get("component_name")
                component_version = request.GET.get("component_version")
                query_component_params ={
                   "project_name":project_name,
                   "asset":asset,
                    "page":page,
                    "limit":limit
                }
                if component_name:
                    query_component_params["component_name"]=component_name
                if component_version:
                    query_component_params["component_version"] = component_version
                component_list,count = web_recongnize.WebRecongnize().query_module_tag(query_component_params)
                return JsonResponse({
                    "code":"0",
                    "msg":"ok",
                    "data":component_list,
                    "count":count
                })
        except Exception as e:
            print("深度识别查询出现异常=="+str(e.__str__()))
            return JsonResponse({
                "code": "-1",
                "msg": "深度识别查询出现异常=="+str(e.__str__())
            })

    def post(self,request):
        try:
           request_type = request.POST.get("type")
           asset = request.POST.get("asset")
           project_name =request.POST.get("project_name")
           component_name =request.POST.get("component_name")
           component_version =request.POST.get("component_version")
           component_type =request.POST.get("component_type")

           description =request.POST.get("description")
           component_params ={
               "project_name":project_name,
               "asset":asset,
               "component_name":component_name,
               "component_version":component_version,
               "component_type":component_type,
               "description":description
           }
           if request_type =="add":
              source_detail = request.POST.get("source_detail")
              component_params["source_detail"]=source_detail
              add_component_results=web_recongnize.WebRecongnize().create_module_tag(component_params)
              if add_component_results:
                  return JsonResponse({
                      "code":"0",
                      "msg":"ok"
                  })
              else:
                  raise Exception("新增组件失败")
           elif request_type =="modify":
               create_source =request.POST.get("create_source")
               if create_source:
                   component_params["create_source"]=create_source
               asset_id = request.POST.get("asset_id") or ""
               if asset_id:
                   component_params["asset_id"]=asset_id
               update_component_results = web_recongnize.WebRecongnize().update_module_tag(component_params)
               if update_component_results:
                    return JsonResponse({
                        "code": "0",
                        "msg": "ok"
                    })
               else:
                   raise  Exception("修改组件失败")
        except Exception as e:
            print("修改/新增组件出现异常"+str(e.__str__()))
            return JsonResponse({
                "code":"-1",
                "msg":"修改/新增组件出现异常"+str(e.__str__())
            })

class SideStationsView(View):
    def post(self,request):
        try:
            project_name = request.POST.get("project_name")
            ip = request.POST.get("asset")
            asset_id = request.POST.get("asset_id")
            if project_name and ip:
                query_params ={
                    "project_name":project_name,
                    "ip":ip,
                    "asset_id":asset_id
                }
                station_list = SideStaionsDao().query_side_stations(query_params)
                return JsonResponse({
                    "code":"0",
                    "msg":"ok",
                    "data":station_list
                })
            else:
                raise Exception("查询旁站参数缺少项目名称/ip")
        except Exception as e:
            return JsonResponse({
                "code": "-1",
                "msg": ""+str(e.__str__()),
                "data": []
            })


class LogoutView(View):
    def get(self,request):
        logout(request)
        print("登出成功")
        return HttpResponseRedirect(LOGIN_URL)


class RunView(View):
    def post(self,request):
        '''
            project_name
            asset_type:1-域名,2-ip,3-service
            ip_type:1-真实ip，2-c段ip
            domain_type:1-主域名,2-子域名
            domain:xx
            ip:xx
            asset_id:资产id
            service:端口的值
            srv_type:端口类型,1-http,2-https,3-other
            port:xx
        :return:json
        '''
        cursor = connection.cursor()
        try:
            project_name = request.POST.get("project_name") or ""
            asset_type =request.POST.get("asset_type") or ""
            asset_id = request.POST.get("asset_id") or ""
            if project_name and asset_type:
                project_id = ProjectDao().query_project_id_by_name(project_name)
                if project_id and asset_type:
                    asset_type =int(asset_type)
                    # redis_connection = get_redis_connection("default")
                    if asset_type ==1 or asset_type =="1":
                        '''
                            域名运行按钮
                        '''
                        domain_type = request.POST.get("domain_type") or ""
                        domain = request.POST.get("domain") or ""
                        if domain_type and domain:
                            if domain_type ==1 or domain_type =="1":
                                '''
                                    主域名运行按钮,设置几个状态到redis中
                                    0-代表还没执行完,1-代表执行中,2-已完成
                                '''
                                sql ="update online_asset_domain set celery_status='1P' where id=%d and domain_type=1"%(int(asset_id))
                                cursor.execute(sql)
                            elif domain_type ==2 or domain_type =="2":
                                '''
                                    子域名运行按钮
                                    asset,asset_type,asset_id,project_id,project_name
                                '''

                                # subdomain_run_button(domain,1,asset_id,project_id,project_name)
                                # redis_connection.hset(project_name, "sub_domain", 2)
                                # redis_connection.hset(project_name, "ip", 0)
                                # redis_connection.hset(project_name, "port_rustscan", 0)
                                # redis_connection.hset(project_name, "service", 0)
                                # redis_connection.hset(project_name, "banner", 0)
                                # redis_connection.hset(project_name, "dirbuster", 0)
                                sql = "update online_asset_domain set celery_status='3P' where id=%d and domain_type=2" % (
                                    int(asset_id))
                                print("run sql =="+str(sql))
                                cursor.execute(sql)
                    elif asset_type ==2 or asset_type =="2":
                        '''
                            ip资产运行按钮
                        '''
                        ip = request.POST.get("ip")
                        ip_type = request.POST.get("ip_type")
                        asset_id = request.POST.get("asset_id")
                        if ip and ip_type and asset_id:
                            if ip_type ==1 or ip_type=="1":
                                '''
                                    真实ip
                                    asset,asset_type,asset_id,project_id,project_name
                                '''
                                # ip_run_button(ip,2,asset_id,project_id,project_name)
                                sql ="update online_asset_ip set celery_status='5P' where id=%d and ip_type=1"%(int(asset_id))
                                cursor.execute(sql)
                            elif ip_type ==4 or ip_type=="4":
                                '''
                                    c段ip
                                    asset,asset_type,asset_id,project_id,project_name
                                '''
                                # crange_run_button(ip,2,asset_id,project_id,project_name)
                                sql = "update online_asset_ip set celery_status='7P' where id=%d and ip_type=4" % (
                                    int(asset_id))
                                cursor.execute(sql)
                            # redis_connection.hset(project_name, "ip", 2)
                            # redis_connection.hset(project_name, "port_rustscan", 0)
                            # redis_connection.hset(project_name, "service", 0)
                            # redis_connection.hset(project_name, "banner", 0)
                            # redis_connection.hset(project_name, "dirbuster", 0)
                    elif asset_type ==3 or asset_type =="3":
                        service = request.POST.get("service") or ""
                        asset_id = request.POST.get("asset_id") or ""
                        srv_type = request.POST.get("srv_type") or ""

                        if service  and asset_id and srv_type:
                            srv_type = int(srv_type)
                            sql =""
                            if srv_type ==1:
                                '''
                                    http端口运行按钮
                                    asset,asset_type,asset_id,project_id,project_name,port,domain,srv_type
                                '''
                                # run_http_port()
                                sql ="update online_asset_service set celery_status='9P' where id=%d and srv_type=1"%(int(asset_id))
                            elif srv_type ==2:
                                '''
                                    https端口运行按钮
                                '''
                                # run_ssl_port(service,asset_id,3,project_id,project_name)
                                sql = "update online_asset_service set celery_status='9P' where id=%d and srv_type=2" % (
                                    int(asset_id))
                            elif srv_type ==3:
                                '''
                                    非web端口运行按钮
                                '''
                                # run_not_web_service_button(service,asset_id,3,project_id,project_name)
                                sql = "update online_asset_service set celery_status='9P' where id=%d and srv_type=9" % (
                                    int(asset_id))
                            cursor.execute(sql)
                            # redis_connection.hset(project_name, "service", 0)
                            # redis_connection.hset(project_name, "banner", 0)
                            # redis_connection.hset(project_name, "dirbuster", 0)
                    return JsonResponse({
                        "code":"0",
                        "msg":"ok"
                    })
        except Exception as e:
            print("运行按钮出现异常=="+str(e.__str__()))
            return JsonResponse({
                "code":"-1",
                "msg":"运行按钮出现异常=="+str(e.__str__())
            })
        finally:
            if cursor:
                cursor.close()
class TaskView(View):
    def get(self,request):
        domain_scheduler(repeat=10)
        domain_worker_schduler(repeat=10)
        ip_scheduler(repeat=10)
        ip_worker_schduler(repeat=10)
        service_scheduler(repeat=10)
        service_worker_schduler(repeat=10)
        return JsonResponse({"code":"0","msg":"ok"})

class TestView(View):
    def get(self,request):
        try:
            from app.module import WhoisInfo,Cdn,SideStations,IPLocation,CDuan,PortScan,PortBanner,WebAsset,ScreenShot,SslInfo,SslFingerPrint,DirBuster
            module_name = request.GET.get("module_name")
            if module_name =="whois_info":
                whois = WhoisInfo(
                    {"domain": "www.sogou.com", "asset_id": 30, "asset_type": 1, "project_id": 1, "project_name": "招商银行渗透项目",
                     "module_name": "whois_info"})
                whois.run()
            elif module_name =="cdn":
                cdn = Cdn({"domain": "dowanload.nucc.com", "asset_id": 30, "asset_type": 1, "project_id": 1,
                           "project_name": "招商银行渗透项目", "module_name": "cdn"})
                cdn.run()
            elif module_name =="side_station":
                side_station = SideStations({"asset": "39.107.196.233","module_name":"side_stations","project_id":1,"project_name":"招商银行渗透项目","asset_type":2,"asset_id":3})
                side_station.run()
            elif module_name =="IP_Location":
                iplocation = IPLocation({"asset": "39.107.196.233","module_name":"side_stations","project_id":1,"project_name":"招商银行渗透项目","asset_type":2,"asset_id":3})
                iplocation.run()
            elif module_name =="crange":
                crange = CDuan(
                    {"asset": "39.107.196.233", "asset_type": 2, "asset_id": 3, "project_id": 1,
                     "module_name": "crange", "project_name": "招商银行渗透项目"})
                crange.run()
            elif module_name =="portscan":
                port_scan = PortScan({"asset": "221.122.73.150", "asset_type": 3, "asset_id": 1,
                                      "project_id": 1, "module_name": "portscan",
                                      "project_name": "招商银行渗透项目", "type": 4})
                port_scan.run()
            elif module_name =="banner":
                portbanner = PortBanner(
                    {"asset": "58.251.78.111", "asset_type": 3, "asset_id": 79, "project_id": 1,
                     "module_name": "portbanner", "project_name": "招商基金", "port": 22})
                portbanner.run()
            elif module_name =="web_recongnize":
                webasset = WebAsset(
                    {"asset": "221.122.73.150","domain":"", "asset_type": 3, "asset_id": 79, "project_id": 1,
                     "project_name": "招商银行渗透项目", "module_name": "webasset", "port": 80,"srv_type":"http"})
                webasset.run()
            elif module_name =="screenshot":
                screenshot = ScreenShot(
                    {"asset": "139.155.75.152", "domain": "www.kerororo.com", "asset_type": 3, "asset_id": 79,
                     "project_id": 1,
                     "project_name": "招商银行渗透项目", "module_name": "webasset", "port": 80, "srv_type": "http"})
                screenshot.run()
            elif module_name =="sslinfo":
                ssl = SslInfo({"asset": "139.155.75.152","domain":"www.kerororo.com", "asset_type": 3, "asset_id": 79, "project_id": 1,
                     "project_name": "招商银行渗透项目", "module_name": "webasset", "port": 443,"srv_type":"https"})
                ssl.run()
            elif module_name =="dirbuster":
                dirbuster = DirBuster({"asset": "58.251.78.175","domain":"", "asset_type": 3, "asset_id": 37, "project_id": 1,
                     "project_name": "招商基金", "module_name": "dirbuster", "port": 443,"srv_type":"https"})
                dirbuster.run()
            elif module_name =="scheduler":
                service_scheduler()
            elif module_name == "worker":
                from app.dao.module_function import ModuleFunctionDao
                from django.db import connection
                import re
                cursor = connection.cursor()
                modulefunctiondao = ModuleFunctionDao()
                result ={'exists_data': False, 'status_code': 2, 'fail_reason': '', 'data': '', 'module_name': 'side_stations', 'asset_type': 2, 'asset_id': 2, 'project_id': 1, 'project_name': '招商基金'}
                asset_id = ""
                project_id = ""
                module_name = ""
                asset_type = ""
                project_name = ""
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
                        update_params["project_name"] = project_name
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
                    modulefunctiondao.update_module_function(update_params)
                if asset_id:
                    '''
                        更新资产的状态,先查询出资产的信息
                    '''
                    select_sql = "select celery_status from online_asset_domain where id=%d" % (int(asset_id))

                    cursor.execute(select_sql)
                    celery_results = cursor.fetchall()

                    if celery_results and len(celery_results) >= 1:
                        celery_status = celery_results[0][0]

                        if celery_status:
                            current_line_res = re.findall("\d+", celery_status, re.S)
                            if current_line_res and len(current_line_res) == 1:
                                update_sql = "update online_asset_domain set celery_status='%s' where id=%d" % (
                                str(current_line_res[0]) + "F", int(asset_id))

                                cursor.execute(update_sql)

            return JsonResponse({"code":"0","msg":"ok"})
        except Exception as e:
            return JsonResponse({"code": "0", "msg": "test view 出现异常=="+str(e.__str__())})



class DirbusterView(View):
    def post(self,request):
        try:
            '''
             "project_name":project_name,
                        "asset_id":id,
                        "asset":ip
            查看端口关联的ip资产表的dirbuster 和ip关联的domain的dirbuster
            :return:
            '''
            project_name =request.POST.get("project_name") or ""
            asset_id = request.POST.get("asset_id") or ""
            asset = request.POST.get("asset") or ""
            if project_name and asset_id and asset:
                dirbuster = {
                    "id":asset_id,
                    "asset":asset,
                    "project_name":project_name
                }
                results =service_dao.ServiceDao().dirbuster(dirbuster)
                print(results)
                return JsonResponse({
                    "code":"0",
                    "msg":"ok",
                    "data":results
                })
        except Exception as e:
            return JsonResponse({
                "code": "-1",
                "msg": "查询爆破目录出现异常=="+str(e.__str__()),
                "data": []
            })


'''
    初始化wapplayer数据到redis中
'''
class RedisInitView(View):
    def get(self,request):
        try:
            BaseSettingsDao().redis_init()
            return JsonResponse({
                "code":"0",
                "msg":"ok",
                "data":""
            })
        except Exception as e:
            return JsonResponse({
                "code": "-1",
                "msg": "redis初始化出现异常=="+str(e.__str__()),
                "data": ""
            })

























