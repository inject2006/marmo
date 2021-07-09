# -*- coding:UTF-8 -*-
'''
    shodan api
'''
import re
import requests
from marmo.settings import SHODAN_API_KEY
from app.dao.marmo_log_dao import MarmoLogDao
class ShoDan_Api():
    def __init__(self,asset_data):
        self.shodan_api_url='https://api.shodan.io/shodan/host/search?key=%s&query=hostname:"%s"'
        self.key=SHODAN_API_KEY
        self.query = asset_data["domain"]
        self.asset_data = asset_data
        self.ips =[]
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    '''
        发起shodan查询    
    '''
    def shodan_query(self):
        # try:
            search_url = self.shodan_api_url%(self.key,self.query)
            self.marmo_log["datas"].append("shodan query url =="+str(search_url))
            search_res = requests.get(search_url)
            if search_res.status_code ==200:
                shodan_json = search_res.json()
                self.marmo_log["datas"].append("shodan query json ==" + str(shodan_json))
                if shodan_json.__contains__("matches"):
                    matches = shodan_json["matches"]
                    for match in matches:
                        if match.__contains__("ip_str"):
                            ip_str =match["ip_str"]
                            self.ips.append(ip_str)


        # except Exception as e:
        #     pass
    def run(self):
        try:
            self.shodan_query()
            self.marmo_log["datas"].append("shodan run datas =="+str(self.ips))
        except Exception as e:
            print("获取shodan结果出现异常=="+str(e.__str__()))
            self.marmo_log["exceptions"].append("获取shodan结果出现异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log数据入库
            '''
            add_log_params = {
                "module": "REAL_IP_SHODAN_API",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.ips




if __name__ =="__main__":
    shodan=ShoDan_Api("baidu.com")
    shodan.run()










