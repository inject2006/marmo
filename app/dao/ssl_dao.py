# -*- coding:UTF-8 -*-
'''
    ssl证书信息
'''
from app.models import SslCertificates
from app.models import MarmoProject
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class SslCertificatesDao():
    def __init__(self):
        pass

    '''
        创建证书信息
    '''
    def create_certificates(self,asset_data):
            project_name = asset_data["project_name"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    add_params ={
                        "info":asset_data["info"],
                        "port": asset_data["port"],
                        "asset": asset_data["asset"],
                        "type": asset_data["type"],
                        "hash":asset_data["hash"],
                        "project_id":int(project_id)
                    }
                    ssl = SslCertificates.objects.create(**add_params)
                    if ssl:
                        return True
                    else:
                        raise Exception("创建ssl证书信息失败")
                else:
                    raise Exception("找不到项目")
            else:
                raise Exception("创建证书信息没有project参数")

    '''
        更新证书信息
    '''
    def update_certificates(self,data):
        project_name = data["project_name"]
        if project_name:
            project_obj = self.query_project_exists_by_name(project_name)
            if project_obj:
                project_id = project_obj.id
                asset=data["asset"]
                port =data["port"]
                ssl_type=data["type"]
                ssl = SslCertificates.objects.filter(project_id=int(project_id),asset=asset,port=port,type=ssl_type).get()
                if ssl:
                    ssl.hash = data["hash"]
                    ssl.save()
                    return True
                else:
                    raise Exception("更新ssl证书信息不存在")
            else:
                raise Exception("找不到项目")
        else:
            raise Exception("创建证书信息没有project参数")


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

