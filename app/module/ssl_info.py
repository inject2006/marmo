# -*- coding:UTF-8 -*-
'''
    获取ssl信息
    两种情况:
       ip:port
       domain:port
'''
import os
import re

from app.dao.ssl_dao import SslCertificatesDao
from marmo.settings import TEMP_FILE_PATH,SSLINFO_COMMAND
from app.dao.marmo_log_dao import MarmoLogDao
from .ssl_fingerprint import SslFingerPrint
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class SslInfo():
    def __init__(self,asset_data):
        self.command =SSLINFO_COMMAND
        self.asset_data = asset_data
        self.domain=asset_data["domain"]
        self.port =asset_data["port"]
        self.asset =asset_data["asset"]
        self.ssl_info =""
        self.file_path ="ssl_info"
        # self.file_name=str(self.asset)+"_"+str(self.port)+".cer"
        self.module_name=asset_data["module_name"]
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


    def run_command(self,asset,port,asset_type):
        command = self.command%(str(asset),str(port))
        self.marmo_log["datas"].append("ssl命令="+str(command))
        logger.log("ssl命令="+str(command))
        command_result =os.popen(command)
        file_name =str(asset) + "_" + str(port) + ".cer"
        self.marmo_log["datas"].append("file name =="+str(file_name))
        ssl_info =""
        for result in command_result:
            ssl_info+=result
        logger.log("results =="+str(ssl_info))
        self.marmo_log["datas"].append("ssl info results =="+str(ssl_info))
        if ssl_info:
            pattern = "-----BEGIN CERTIFICATE-----(.*?)-----END CERTIFICATE-----"
            res = re.findall(pattern, ssl_info, re.S)
            if res and len(res) >= 1:
                centrificate = res[0]
                centrificate_before = "-----BEGIN CERTIFICATE-----" + centrificate
                centrificate_after = centrificate_before + "-----END CERTIFICATE-----"
                self.marmo_log["datas"].append("证书=" + str(centrificate_after))
                self.data_info["exists_data"] = True
                self.data_info["status_code"] = 2
                self.data_info["data"] = self.data_info["data"]+centrificate_after
                file_path = os.path.join(TEMP_FILE_PATH, self.file_path)
                if not os.path.exists(file_path):
                    os.system("mkdir -p %s" % (file_path))
                file_name_path = os.path.join(file_path, file_name)
                self.marmo_log["datas"].append("file name path ==="+str(file_name_path))
                with open(file_name_path, "w", encoding="UTF-8") as f:
                    f.write(centrificate_after)
                    f.flush()
                '''
                    调用sslprint获取证书信息
                '''
                hash = SslFingerPrint().run_command(file_name_path,int(self.asset_data["asset_id"]))
                self.marmo_log["datas"].append("ssl finger print hash =="+str(hash))
                '''
                    插入ssl信息到ssl_certificates
                '''
                ssl_dao = SslCertificatesDao()
                add_params = {
                    "info": str(centrificate_after),
                    "port": port,
                    "asset": asset,
                    "type": asset_type,
                    "hash":hash,
                    "project_name": self.asset_data["project_name"]
                }
                self.marmo_log["datas"].append("ssl finger update params ==" + str(add_params))
                ssl_dao.create_certificates(add_params)
            else:
                logger.log("asset %s %s 没有证书信息"%(asset,str(port)))
                self.marmo_log["datas"].append("asset %s %s 没有证书信息"%(asset,str(port)))



    '''
        run函数
    '''
    def run(self):
        try:
            if self.domain and self.port:
                self.run_command(self.domain,self.port,1)

            if self.asset and self.port:
                self.run_command(self.asset, self.port, 2)
        except Exception as e:
            print("获取ssl信息失败=="+str(e.__str__()))
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
            self.data_info["fail_reason"]="获取ssl信息失败=="+str(e.__str__())
            self.marmo_log["exceptions"].append("获取ssl信息失败=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "SSLINFO",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info



if __name__ =="__main__":
    ssl =SslInfo()
    ssl.run()








