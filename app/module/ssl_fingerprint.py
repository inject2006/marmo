# -*- coding:UTF-8 -*-
'''
    获取服务器证书指纹
'''
import os
import re
from app.dao.marmo_log_dao import MarmoLogDao
from marmo.settings import SSLFINGERPRINT_COMMAND
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class SslFingerPrint():
    def __init__(self):
        self.command=SSLFINGERPRINT_COMMAND
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    '''
        执行命令
    '''
    def run_command(self,file_path,asset_id):
        hash=""
        try:
            # file_name = os.path.join(self.file_path,self.domain+".cer")
            self.marmo_log["datas"].append("ssl finger print file path ==" + str(file_path))
            if not os.path.exists(file_path):
                raise Exception("证书文件不存在")

            command = self.command%(file_path)
            results =os.popen(command)
            hash_info = ""
            for result in results:
                hash_info+=result
            self.marmo_log["datas"].append("hash info =="+str(hash_info))
            if hash_info:
                pattern ="(.*?)-----BEGIN CERTIFICATE-----"
                res = re.findall(pattern,hash_info,re.S)
                if res and len(res) >=1:
                    hash = res[0]
                    self.marmo_log["datas"].append("hash =="+str(hash))
                    # self.data_info["exists_data"]=True
                    # self.data_info["data"]=str(hash)
                    # self.data_info["status_code"]=2
                #     return hash
                # else:
                #     return ""
            # else:
            #     return  ""
        except Exception as e:
            logger.log("ssl finger print 出现异常=="+str(e.__str__()))
            self.marmo_log["exceptions"].append("ssl finger print 出现异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "SSLFINGERPRINT",
                "type": '3',
                "module_log": str(self.marmo_log),
                "asset_id": asset_id
            }
            MarmoLogDao().add_log(add_log_params)
            return hash









