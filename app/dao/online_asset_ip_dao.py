# -*- coding:UTF-8 -*-
'''
    ip表操作
'''
from app.models import OnlineAssetIp
from app.utils.marmo_logger import Marmo_Logger
from app.models import MarmoProject
logger =Marmo_Logger()
from django.db import connection
import json
class OnlineAssetIpDao():
    def __init__(self):
        pass

    '''
        ip表更新ip字段
    '''
    def upate_location(self,data):
        try:
            project_name = data["project_name"]
            project_obj = self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                ip =data["ip"]
                asset_id =data["asset_id"]
                location =data["location"]
                if ip and project_id and asset_id:
                    onlineassetip =OnlineAssetIp.objects.filter(ip=ip,project_id=int(project_id),id=asset_id).get()
                    onlineassetip.location =location
                    onlineassetip.save()
                else:
                    raise Exception("更新ip资产位置信息异常")
        except Exception as e:
            raise Exception("更新ip资产位置信息异常=="+str(e.__str__()))

    '''
        更新dirbuster字段,形式是追加
    '''
    def update_dirbuster(self,data):
        try:
            project_name = data["project_name"]
            project_obj = self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                ip = data["ip"]
                asset_id = data["asset_id"]  #这个id是端口的id
                dirbuster = data["dirbuster"]
                if ip and project_id and asset_id:
                    onlineassetip = OnlineAssetIp.objects.filter(ip=ip, project_id=int(project_id)).get()
                    temp_dirbuster =onlineassetip.dirbuster
                    if temp_dirbuster =="None" or temp_dirbuster ==None:
                        temp_dirbuster =""
                    onlineassetip.dirbuster = temp_dirbuster+"#@#"+json.dumps(dirbuster)
                    onlineassetip.save()
                else:
                    raise Exception("更新ip资产位置信息异常")
        except Exception as e:
            raise Exception("更新ip资产位置信息异常==" + str(e.__str__()))



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
        查询出项目的所有cdn_ip 和c段的ip
    '''
    def get_cduan_and_cdnIp(self,data):
        try:
            project_name = data["project_name"]
            project_obj = self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                cduan_ip_list =[]
                '''
                    查询出c段IP
                '''
                cduan_list_results = OnlineAssetIp.objects.filter(ip_type=4,project_id=int(project_id))[:]
                for cduan in cduan_list_results:
                    ip = cduan.ip
                    cduan_ip_list.append(ip)
                cdn_ip_list=[]
                '''
                    查询出cdn-ip
                '''
                cdn_list_results = OnlineAssetIp.objects.filter(ip_type=2,project_id=int(project_id))[:]
                for cdn in cdn_list_results:
                    ip = cdn.ip
                    cdn_ip_list.append(ip)
                return cdn_ip_list,cduan_ip_list
        except Exception as e:
            raise Exception("获取项目的c段IP和cdn IP列表出现异常="+str(e.__str__()))


    '''
        查询ip对应的域名
        input:cdn ip列表
    '''
    def ip_related_domain(self,ip_list):
        cursor=None
        try:
            ip_and_domain_list =[]
            cursor = connection.cursor()
            for ip in ip_list:
                ip_and_domain_obj ={}
                sql ="select domain.domain_name,domain.id from online_asset_domain domain,online_asset_ip ip,domain_ip_relation dir where domain.id=dir.asset_domain_id and ip.id=dir.asset_ip_id and ip.ip=%s"%(ip)
                cursor.execute(sql)
                result = cursor.fetchone()
                if result and len(result) >=1:
                    ip_and_domain_obj["domain"]=result[0]
                    ip_and_domain_obj["id"] = result[1]
                    ip_and_domain_obj["ip"]=ip
                    ip_and_domain_list.append(ip_and_domain_obj)
            if cursor:
                cursor.close()
            return ip_and_domain_list
        except Exception as e:
            print("获取cdn ip对应的域名错误=="+str(e.__str__()))
            if cursor:
                cursor.close()
            raise Exception("获取cdn ip对应的域名错误=="+str(e.__str__()))





