# -*- coding:UTF-8 -*-
'''
    gobuster爆破
'''
import os
from marmo.settings import GOBUSTER_FILEPATH,GOBUSTER_COMMAND
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()

class GoBuster():
    def __init__(self,asset_data):
        self.domain=asset_data["domain_name"]
        self.file_path=GOBUSTER_FILEPATH
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }
        self.domain_set = set()
        self.asset_data=asset_data
        self.marmo_log =""
        self.wordlist="/usr/share/wordlists/dirb"

    def run_command(self):
        try:
            # cmd_command ="/usr/local/gopath/bin/gobuster dns  -t 50 -d %s -w /data/dns_final.txt -o %s"%(self.domain,self.file_path+self.domain+".txt")
            cmd_command = GOBUSTER_COMMAND%(self.domain,self.file_path+self.domain+".txt")
            self.marmo_log["datas"].append("gobuster 执行命令=="+str(cmd_command))
            run_code=os.system(cmd_command)
            if run_code ==0 or run_code =="0":
                return  True
            else:
                return False
        except Exception as e:
            logger.log("执行goBuster出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("执行goBuster出现异常==="+str(e.__str__()))
            raise Exception("执行goBuster出现异常==="+str(e.__str__()))

    '''
        读取gobuster命令执行结果
    '''
    def read_goBuster(self):
        try:
            file_path = os.path.join(self.file_path,self.domain+".txt")
            with open(file_path,"r",encoding="UTF-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line and "Found:" in line:
                        found_domains =line.replace("Found:","")
                        if found_domains:
                            self.domain_set.add(found_domains.lower())
            self.marmo_log["datas"].append("goBuster执行结果="+str(self.domain_set))
        except Exception as e:
            logger.log("read gobuster result error=="+str(e.__str__()))
            self.marmo_log["exceptions"].append("read gobuster result error=="+str(e.__str__()))
            raise Exception("read gobuster result error=="+str(e.__str__()))



    def run(self):
        try:
            run_commands = self.run_command()
            if run_commands:
                return self.read_goBuster()
        except Exception as e:
            logger.log("goBuster run函数出现异常=="+str(e.__str__))
            self.marmo_log["exceptions"].append("goBuster run函数出现异常=="+str(e.__str__))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "GoBuster",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.domain_set

if __name__ =="__main__":
    gobuster= GoBuster("","")
    gobuster.run()




