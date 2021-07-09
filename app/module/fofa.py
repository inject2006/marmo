# -*- coding:UTF-8 -*-
'''
    fofa搜索引擎
    输入:{domain,asset_id}
'''
import requests
import base64
from marmo.settings import FOFA_EMAIL,FOFA_KEY
from app.dao.marmo_log_dao import MarmoLogDao
class FofaClient:
    def __init__(self,asset_data):
        '''
        "sec@smartservice.com.cn","bfaec2da79d0955518c6beb581e09f47"
        :param domain:
        '''
        self.email = FOFA_EMAIL
        self.key =FOFA_KEY
        self.base_url = "https://fofa.so"
        self.search_api_url = "/api/v1/search/all?email=%s&full=%s&key=%s&qbase64=%s"
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        self.domain=asset_data["domain"]
        self.asset_data = asset_data
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    def fofa_search_all(self, query):
        qbase64 = base64.b64encode(query.encode())
        param = {
            "email": self.email,
            "key": self.key,
            "qbase64": qbase64.decode('utf-8'),
            "size": self.page_size
        }

        self.param = param
        data =  self._api(self.base_url + self.search_api_url)
        return data

    def getBase64Domain(self):
        try:
            query ='domain="%s"'%(self.domain)
            self.marmo_log["datas"].append(str(query))
            query_base64=base64.b64encode(query.encode(encoding="UTF-8"))
            self.marmo_log["datas"].append("getBase64Domain=="+str(query))
            return query_base64.decode(encoding="UTF-8")
        except Exception as e:
            print("getBase64Domain 出现异常+=="+str(e.__str__()))

    def _api(self,full):

        url = (self.base_url+self.search_api_url)%(self.email,full,self.key,self.getBase64Domain())
        self.marmo_log["datas"].append("fofa url =="+str(url))
        fofa_res = requests.get(url,headers=self.headers)
        if fofa_res.status_code ==200:
           fofa_data = fofa_res.json()
           self.marmo_log["datas"].append("fofa data =="+str(fofa_data))
           if fofa_data.__contains__("error"):
               error = fofa_data["error"]
               if not error:
                   results = fofa_data["results"]
                   return results
           else:
               self.marmo_log["datas"].append("fofa查询出现异常==="+str(fofa_res.status_code))
               return []
        else:
            return []


    def search_cert(self, cert):
        query = 'cert="{}"'.format(cert)
        data = self.fofa_search_all(query)
        if data["error"] and data["errmsg"]:
            raise Exception(data["errmsg"])

        results = data["results"]
        return results

    '''
        执行
    '''
    def run(self):
        try:
            fofa= self._api(True)
            self.marmo_log["datas"].append("run result =="+str(fofa))
        except Exception as e:
            self.marmo_log["exceptions"].append("fofa run error =="+str(e.__str__()))
        finally:
            '''
                marmo_log数据入库
            '''
            add_log_params = {
                "module": "REAL_IP_FOFA",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return fofa

if __name__ =="__main__":
    fofa = FofaClient({"domain":"nucc.com","asset_id":1})
    fofa.run()
