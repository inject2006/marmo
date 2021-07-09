# -*- coding:UTF-8 -*-
'''
    实现whois_info信息收集
    日志形式
    {
        exists_data:True/False
        status:0-5,
        error_reason:错误原因,
        text:日志
    }
'''
import os
from .dao.marmo_log_dao import MarmoLogDao
from .dao.asset_dao import AssetDao
from .utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
from django.test import TestCase
class WhoisInfo(TestCase):
    def __init__(self,asset_data):
        self.domain = asset_data["domain"]
        self.command ="whois %s -H"
        self.module_data = asset_data
        self.module_name =asset_data["module_name"]
        self.data_info = {
            "exists_data": False,
            "status_code": "",
            "fail_reason": "",
            "data": "",
            "module_name": self.module_name,
            "asset_type": asset_data["asset_type"],
            "asset_id": asset_data["asset_id"],
            "project_id": asset_data["project_id"],
            "project_name": asset_data["project_name"]
        }
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }
        self.whois_result=""


    def run(self):
        try:
            command = self.command%(self.domain)
            logger.log("whois info command ="+str(command))
            self.marmo_log["datas"].append("whois执行命令="+str(command))
            whois_info=os.popen(command)
            for result in whois_info:
                self.whois_result+=result
            logger.log("whois info结果=="+str(self.whois_result))
            self.marmo_log["datas"].append("执行whois_info结果="+str(self.whois_result))

            '''
                更新域名的whois_info字段
            '''
            if self.whois_result:
                self.data_info["exists_data"]=True
                self.data_info["status_code"]=2
                self.data_info["data"]=self.whois_result
            else:
                self.data_info["status_code"] = 2
            '''
            插入数据
            '''
            update_asset_params ={
               "domain_id":self.module_data["asset_id"],
               "whois_info":str(whois_info),
               "project_id":self.module_data["project_id"]
            }
            update_result=AssetDao().update_domain_asset(update_asset_params)

        except Exception as e:
            print("插入数据出现异常==="+str(e.__str__()))
            self.data_info["exists_data"]=False
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="whois_info信息收集出现异常="+str(e.__str__())
            self.marmo_log["exceptions"].append("whois_info信息收集出现异常="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "WHOIS_INFO",
                "type": '2',
                "module_log": str(self.marmo_log)
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info

if __name__ =="__main__":
    whois = WhoisInfo({"domain":"im.nucc.com","asset_id":30,"asset_type":1,"project_id":1,"project_name":"招商银行渗透项目","module_name":"whois_info"})
    whois.run()








