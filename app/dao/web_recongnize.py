# -*- coding:UTF-8
'''
    web深度识别模块
'''
from app.models import ComponentTag,ModuleFunction,MarmoProject
from django.db import connection
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
class WebRecongnize():
    '''
        查询web深度识别
    '''
    def query_module_tag(self,data):
        cursor = connection.cursor()
        try:
            project_name = data["project_name"]
            if project_name:
                print(project_name)
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    page = data["page"]
                    limit =data["limit"]
                    page_start=(int(page)-1)*int(limit)
                    project_id = int(project_obj.id)
                    count_sql = "select count(1) count from component_tag where project_id=%d and asset='%s'" % (project_id,data["asset"])
                    select_sql = "select * from component_tag where project_id=%d and asset='%s'" % (project_id,data["asset"])
                    if data.__contains__("component_name"):
                        select_sql+=" and component_name like '%"+data["component_name"]+"%'"
                        count_sql+=" and component_name like '%"+data["component_name"]+"%'"
                    if data.__contains__("component_version"):
                        select_sql +=" and version like '%"+data["component_version"]+"%'"
                        count_sql+=" and version like '%"+data["component_version"]+"%'"
                    select_sql+=" limit %d,%d"%(page_start,int(limit))
                    print(select_sql)
                    print(count_sql)
                    cursor.execute(select_sql)
                    module_results = cursor.fetchall()
                    cursor.execute(count_sql)
                    count =cursor.fetchall()[0]
                    module_list =[]
                    for module in module_results:
                        module_obj={}
                        module_obj["id"]=module[0]
                        module_obj["component_name"]=module[1]
                        module_obj["version"] = module[2]
                        module_obj["component_type"] = module[3]
                        module_obj["create_source"] = module[4]
                        module_obj["source_detail"]=module[5]
                        module_obj["description"]=module[7]
                        module_obj["asset"]=module[8]
                        module_obj["create_time"] = module[9]
                        module_list.append(module_obj)
                    return module_list,count
        except Exception as e:
            logger.log("查询模块出现异常==="+str(e.__str__()))
            raise Exception("查询模块出现异常==="+str(e.__str__()))


    '''
        修改module_tag
        id,project_id
    '''
    def update_module_tag(self,data):
        try:
            logger.log("更新module tag params =="+str(data))
            project_name = data["project_name"]
            if project_name:
                print(project_name)
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = int(project_obj.id)
                    update_params ={
                        "project_id":project_id,
                        "component_name":data["component_name"],
                        "version":data["component_version"],
                        "component_type":data["component_type"],
                        "create_source":data["create_source"],
                        "description":data["description"],
                        "asset":data["asset"]
                    }
                    asset_id = data["asset_id"]
                    if asset_id:
                        module_tag =ComponentTag.objects.filter(project_id=update_params["project_id"],component_name=update_params["component_name"],asset=update_params["asset"],id=int(asset_id)).get()
                        if module_tag:
                            module_tag.module_name = update_params["component_name"]
                            module_tag.version=update_params["version"]
                            module_tag.module_type = update_params["component_type"]
                            module_tag.create_source = update_params["create_source"]
                            module_tag.description = update_params["description"]
                            module_tag.save()
                            return True
                        else:
                            raise Exception("组件不存在")
        except ComponentTag.DoesNotExist:
            raise Exception("修改组件不存在")
        except Exception as e:
            logger.log("修改组件标签出现异常=="+str(e.__str__()))
            raise Exception("修改组件标签出现异常=="+str(e.__str__()))



    '''
        新增模块标签
        "type":"add",
        "project_name":project_name,
        "asset":asset,
        "component_name":component_name,
        "component_version":component_version,
        "component_type":component_type,
        "source_detail":source_detail,
        "description":description
    '''
    def create_module_tag(self,data):
        try:
            project_name = data["project_name"]
            if project_name:
                print(project_name)
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = int(project_obj.id)
                    create_params = {
                        "project_id": project_id,
                        "component_name": data["component_name"],
                        "version": data["component_version"],
                        "component_type": data["component_type"],
                        "create_source": "manual",
                        "description": data["description"],
                        "source_detail":data["source_detail"],
                        "asset":data["asset"]
                    }
                    module_tag = ComponentTag.objects.create(**create_params)
                    if module_tag:
                        return True
                    else:
                        return False
        except Exception as e:
            logger.log("创建模块标签出现异常=="+str(e.__str__()))
            raise Exception("创建模块标签出现异常=="+str(e.__str__()))

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







