# -*- coding:UTF-8 -*-
'''
    漏洞
'''
from app.models import VulnInfo,MarmoProject
from app.utils.marmo_logger import Marmo_Logger

from django.db import connection
logger = Marmo_Logger()
class VulnInfoDao():
    '''
        新增漏洞,漏洞状态为待确认
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
    def create_vuln_info(self,data):
        try:
            project_name =data["project_name"]
            if project_name:
                project_obj =self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    create_vuln_info_obj={
                        "vuln_name":data["vuln_name"],
                        "vuln_level":int(data["vuln_level"]),
                        "vuln_details": data["vuln_details"],
                        "vuln_affect": data["vuln_affect"],
                        "vuln_status": 4,
                        "is_retest": 2,
                        "project_id":int(project_id),
                        "user_id": int(data["user_id"]),
                        "asset_type": int(data["asset_type"]),
                        "asset":data["asset"]
                    }
                    vuln_info =VulnInfo.objects.create(**create_vuln_info_obj)
                    if vuln_info:
                        return True
                    else:
                        return False
            else:
                raise Exception("新增漏洞缺少项目名称")
        except Exception as e:
            logger.log("创建漏洞出现异常=="+str(e.__str__()))
            raise Exception("创建漏洞出现异常=="+str(e.__str__()))


    '''
        修改漏洞
        "vuln_name": vuln_name,
                    "vuln_level": vuln_level,
                    "vuln_affect": vuln_affect,
                    "vuln_details": vuln_details,
                    "vuln_status": vuln_status,
                    "is_retest": is_retest,
                    "vuln_desc": vuln_desc,
                    "project_name": project_name
    '''
    def update_vuln_info(self,data):
        try:
            project_name = data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    update_vuln_info_obj = {
                        "vuln_name": data["vuln_name"],
                        "vuln_level": int(data["vuln_level"]),
                        "vuln_desc": data["vuln_desc"],
                        "vuln_details": data["vuln_details"],
                        "vuln_affect": data["vuln_affect"],
                        "vuln_status": int(data["vuln_status"]),
                        "is_retest": int(data["is_retest"])
                    }
                    vuln = VulnInfo.objects.filter(vuln_name=update_vuln_info_obj["vuln_name"],project_id=int(project_id)).get()
                    if vuln:
                        vuln.vuln_name = update_vuln_info_obj["vuln_name"]
                        vuln.vuln_level = update_vuln_info_obj["vuln_level"]
                        vuln.vuln_desc = update_vuln_info_obj["vuln_desc"]
                        vuln.vuln_details = update_vuln_info_obj["vuln_details"]
                        vuln.vuln_affect = update_vuln_info_obj["vuln_affect"]
                        vuln.vuln_status = update_vuln_info_obj["vuln_status"]
                        vuln.is_retest = update_vuln_info_obj["is_retest"]
                        vuln.save()
                        return True
                    else:
                        raise Exception("漏洞不存在")
        except Exception as e:
            logger.log("修改漏洞出现异常"+str(e.__str__()))
            raise Exception("修改漏洞出现异常"+str(e.__str__()))

    '''
        查询和项目关联的漏洞
    '''
    def query_vlun_info(self,data):
        cursor = connection.cursor()
        try:
            if data.__contains__("project_name"):
                project_name = data["project_name"]
            else:
                project_name =""
            #project_name = data["project_name"]
            page = data["page"]
            limit = data["limit"]
            asset = data["asset"]
            asset_type =data["asset_type"]
            page_start=(int(page)-1)*int(limit)
            page_end=page_start+int(limit)
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    count_sql = "select count(1) count  from vuln_info v,user u where v.user_id=u.id and v.project_id=%d"%(int(project_id))
                    select_sql ="select v.id,v.vuln_name,v.vuln_level,v.vuln_desc,v.vuln_details,v.vuln_affect,v.vuln_status,v.is_retest,v.asset,u.nickname,v.create_time,project.name project_name from vuln_info v,user u,marmo_project project where v.user_id=u.id and v.project_id=project.id and v.project_id=%d"%(int(project_id))
                    if asset:
                        select_sql+=" and v.asset='%s'"%(asset)
                    if asset_type:
                        select_sql+=" and v.asset_type=%d "%(int(asset_type))
                    select_sql+=" limit %d,%d"%(page_start,page_end)
                    print(select_sql)
                    cursor.execute(select_sql)
                    vuln_info_results =cursor.fetchall()
                    cursor.execute(count_sql)
                    count = cursor.fetchall()[0]
                    vuln_info_list =[]
                    for vuln_info in vuln_info_results:
                        vuln_info_obj ={}
                        vuln_info_obj["id"]=vuln_info[0]
                        vuln_info_obj["vuln_name"]=vuln_info[1]
                        vuln_info_obj["vuln_level"] = vuln_info[2]
                        vuln_info_obj["vuln_desc"] = vuln_info[3]
                        vuln_info_obj["vuln_details"] = vuln_info[4]
                        vuln_info_obj["vuln_affect"] = vuln_info[5]
                        vuln_info_obj["vuln_status"] = vuln_info[6]
                        vuln_info_obj["is_retest"] = vuln_info[7]
                        vuln_info_obj["asset"] = vuln_info[8]
                        vuln_info_obj["create_user"]=vuln_info[9]
                        vuln_info_obj["create_time"]=vuln_info[10]
                        vuln_info_obj["project_name"]=vuln_info[11]
                        vuln_info_list.append(vuln_info_obj)
                    return vuln_info_list,count
            else:
                '''
                    从左侧菜单进入,全部漏洞查询
                '''
                select_sql = "select v.id,v.vuln_name,v.vuln_level,v.vuln_desc,v.vuln_details,v.vuln_affect,v.vuln_status,v.is_retest,v.asset,u.nickname,v.create_time,project.name project_name from vuln_info v,user u,marmo_project project where v.user_id=u.id and project.id=v.project_id  limit %d,%d"%(page_start,page_end)
                count_sql ="select count(1) count from vuln_info"
                print(select_sql)
                cursor.execute(select_sql)
                vuln_info_results = cursor.fetchall()
                cursor.execute(count_sql)
                count = cursor.fetchall()[0]
                vuln_info_list = []
                for vuln_info in vuln_info_results:
                    vuln_info_obj = {}
                    vuln_info_obj["id"] = vuln_info[0]
                    vuln_info_obj["vuln_name"] = vuln_info[1]
                    vuln_info_obj["vuln_level"] = vuln_info[2]
                    vuln_info_obj["vuln_desc"] = vuln_info[3]
                    vuln_info_obj["vuln_details"] = vuln_info[4]
                    vuln_info_obj["vuln_affect"] = vuln_info[5]
                    vuln_info_obj["vuln_status"] = vuln_info[6]
                    vuln_info_obj["is_retest"] = vuln_info[7]
                    vuln_info_obj["asset"] = vuln_info[8]
                    vuln_info_obj["create_user"] = vuln_info[9]
                    vuln_info_obj["create_time"] = vuln_info[10]
                    vuln_info_obj["project_name"] = vuln_info[11]
                    vuln_info_list.append(vuln_info_obj)
                return vuln_info_list, count

        except Exception as e:
            logger.log("查询漏洞信息出现异常+=="+str(e.__str__()))
            raise Exception("查询漏洞信息出现异常+=="+str(e.__str__()))

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






