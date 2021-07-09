# -*- coding:UTF-8 -*-
'''
    CNAME
'''
import requests
import re
from app.dao.marmo_log_dao import MarmoLogDao
class IpCname():
    def __init__(self,asset_data):
        self.headers ={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }
        self.url ="https://tools.ipip.net/cdn.php"
        self.node="633"
        self.host=asset_data["domain"]
        self.asset_data = asset_data
        self.domains =[]
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }


    def make_request_headers(self):
        assert self.headers
        self.headers["Host"]="tools.ipip.net"
        self.headers["Origin"]="https://tools.ipip.net"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Referer"] = "https://tools.ipip.net/cdn.php"
        self.headers["sec-ch-ua"]='" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"'
        self.headers["sec-ch-ua-mobile"]="?0"
        self.headers["Sec-Fetch-Dest"] = "document"
        self.headers["Sec-Fetch-Mode"] = "navigate"
        self.headers["Sec-Fetch-Site"] = "same-origin"
        self.headers["Sec-Fetch-User"]="?1"
        self.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        self.headers["Accept-Language"] = "zh-CN,zh;q=0.9"

    '''
        请求
    '''
    def run(self):
        try:
            data ={
                "node":(None,str(self.node)),
                "host":(None,str(self.host))
            }
            self.marmo_log["datas"].append("cname data =="+str(data))
            ip_res = requests.post(self.url,headers=self.headers,files=data)
            if ip_res.status_code ==200:
                ip_html=ip_res.text
                self.marmo_log["datas"].append("cname ip res =="+str(ip_html))
                self.parse_html(ip_html)
        except Exception as e:
            print("parse_html 出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("parse_html 出现异常==="+str(e.__str__()))
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
            return self.domains


    '''
        解析网页内容，获取cname的值
    '''
    def parse_html(self,result):
        try:
            pattern='<tr>(.*?)</tr>'
            res = re.findall(pattern,result,re.S)
            if res and len(res) >=1:
                cname_pattern ='<td>(.*?)</td>'
                for td in res:
                    tds = re.findall(cname_pattern,td,re.S)
                    td_result =''
                    for td in tds:
                        td_result+=td.strip()+"|"
                    if td_result:
                        self.domains.append(td_result)
            else:
                return ""
        except Exception as e:
            print("parse_html 出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("parse_html 出现异常==="+str(e.__str__()))




if __name__ =="__main__":
    cname = IpCname("mbap.abchina.com")
    cname.run()
