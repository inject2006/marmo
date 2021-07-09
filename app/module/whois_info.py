# -*- coding:UTF-8 -*-
'''
    实现whois_info信息收集
    输入格式要求:只能是二级域名,比如baidu.com,三级或以上域名不行。
    衍生出的需求:需要对输入的参数进行截取
    命令:whois baidu.com -H

    日志形式
    {
        exists_data:True/False
        status:0-5,
        error_reason:错误原因,
        text:日志
    }
'''
import os
from app.dao.marmo_log_dao import MarmoLogDao
from app.dao.asset_dao import AssetDao
import json
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class WhoisInfo():
    def __init__(self,asset_data):
        self.domain = asset_data["domain"]
        self.command ="whois %s -H"
        self.module_data = asset_data
        self.module_name =asset_data["module_name"]
        self.data_info = {
            "exists_data": False,
            "status_code": 2,
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
        '''
            命令执行结果
        '''
        self.whois_result=""


    def run(self):
        try:
            self.marmo_log["datas"].append("whois info domain %s"%(str(self.domain)))
            real_domain =""
            if "." in self.domain:
                domain_list = self.domain.split(".")
                if len(domain_list) ==2:
                    real_domain = self.domain
                else:
                    '''
                        只获取2-3位,比如www.baidu.com,只获取baidu.com
                    '''
                    if len(domain_list) >=3:
                        real_domain=domain_list[1]+domain_list[2]

            command = self.command%(real_domain)
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
               "whois_info":str(self.whois_result),
               "project_id":self.module_data["project_id"]
            }
            logger.log("插入数据=="+str(update_asset_params))
            self.data_info["datas"].append("更新whois_info参数=="+str(update_asset_params))
            update_result=AssetDao().update_domain_asset(update_asset_params)

        except Exception as e:
            print("whois_info插入数据出现异常==="+str(e.__str__()))
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
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info

if __name__ =="__main__":
    whois = WhoisInfo()
    whois.run("www.baidu.com",{})








