# -*- coding:UTF-8 -*-
'''
    证书查询认证
    返回:[ip1,ip2]
    输入:{domain:"xxx"}
'''

import base64
import requests
import json
from marmo.settings import CENSYS_API_ID,CENSYS_API_SECRET
from app.dao.marmo_log_dao import MarmoLogDao
class CenSysApi():
    def __init__(self,asset_data):
        self.search_url ="https://censys.io/api/v1/search/%s"
        self.domain=asset_data["domain"]
        self.asset_data = asset_data
        self.id=CENSYS_API_ID
        self.secret=CENSYS_API_SECRET
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        self.ips =[]
        self.finger =[]
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    '''
        生成authorization    
    '''
    def authorization(self):
        assert self.id
        assert self.secret
        authorization =base64.b64encode((self.id+":"+self.secret).encode(encoding="UTF-8"))
        authorization="Basic "+authorization.decode(encoding="UTF-8")
        self.marmo_log["datas"].append("authorization =="+str(authorization))
        self.headers["Authorization"]=authorization

    '''
        请求域名访问finger_print
    '''
    def domain_search(self):
        try:
            url = self.search_url%("certificates")
            self.marmo_log["datas"].append("search url =="+str(url))
            data ={
                "query":"parsed.names: %s and tags.raw: trusted"%(self.domain),
                "fields":["parsed.fingerprint_sha256"]
            }
            headers = self.headers
            headers["Content-Type"]="application/json"
            search_response = requests.post(url,data=json.dumps(data),headers=headers)
            if search_response.status_code ==200:
                search_json = search_response.json()
                self.marmo_log["datas"].append("domain search json =="+str(search_json))
                return self.parse_finger(search_json)
        except Exception as e:
            print("domain search出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("domain search出现异常==="+str(e.__str__()))
            return ""

    '''
        解析fingerprint_sha256的值
    '''
    def parse_finger(self,search_json):
        try:
            if search_json.__contains__("status"):
                status = search_json["status"]
                if status == "ok":
                    results = search_json["results"]
                    for result in results:
                        self.finger.append(result["parsed.fingerprint_sha256"])
        except Exception as e:
            print("parse_finger 出现异常===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("parse_finger 出现异常===" + str(e.__str__()))
            return []


    '''
        访问ipv4
    '''
    def ipv4_search(self,sha256):
        try:

            url = self.search_url%("ipv4")
            self.marmo_log["datas"].append("ipv4 search url =="+str(url))
            data ={
                "query":"%s"%(sha256),
                "fields":["ip"]
            }
            self.marmo_log["datas"].append("ipv4 search data =="+str(data))
            search_response = requests.post(url,data=json.dumps(data),headers=self.headers)
            if search_response.status_code ==200:
                search_json = search_response.json()
                print("ip search json =="+str(search_json))
                self.marmo_log["datas"].append("ip search json =="+str(search_json))
                self.parse_ipv4(search_json)
        except Exception as e:
            print("ipv4_search出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("ipv4_search出现异常==="+str(e.__str__()))
            return ""


    '''
        解析ipv4结果
    '''
    def parse_ipv4(self,search_json):
        try:
            if search_json.__contains__("status"):
                status = search_json["status"]
                if status == "ok":
                    results = search_json["results"]
                    for result in results:
                        self.ips.append(result["ip"])
        except Exception as e:
            print("parse_ipv4 出现异常===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("parse_ipv4 出现异常===" + str(e.__str__()))
            return []

    '''
        遍历sha4
    '''
    def circle_sha(self,sha_list):
        try:
            for sha in sha_list:
                self.ipv4_search(sha)
        except Exception as e:
            print("circle_sha 出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("circle_sha 出现异常==="+str(e.__str__()))


    '''
        启动
    '''
    def run(self):
        try:
            self.authorization()
            self.domain_search()
            self.marmo_log["datas"].append("censys api data =="+str(self.finger))
            for ipfinger in self.finger:
                self.ipv4_search(ipfinger)
            self.marmo_log["datas"].append("ip list ==="+str(self.ips))
        except Exception as e:
            self.marmo_log["exceptions"].append("censys 出现异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "REAL_IP_CENSYS_API",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.ips



if __name__ =="__main__":
    censys =CenSysApi({"domain":"139.155.75.152"})
    censys.run()
