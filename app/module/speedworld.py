# -*- coding:UTF-8 -*-
'''
国外多地ping
'''
import execjs
import time
import requests
import re
from scrapy.selector import Selector
from app.dao.marmo_log_dao import MarmoLogDao
class SpeedWorld():
    def __init__(self,asset_data):
        self.headers ={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }
        self.main_url="https://tool.chinaz.com/speedworld/%s"
        self.query_url="https://tool.chinaz.com/iframe.ashx?t=ping&callback=%s"
        self.vb =int(time.time())*1000
        self.domain=asset_data["domain"]
        self.asset_data = asset_data
        self.ips =[]
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }

    def run(self):
        try:
            self.main()
            self.marmo_log["datas"].append(self.ips)
            return self.ips
        except Exception as e:
            self.marmo_log["exceptions"].append("speed world run error=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "REAL_IP_SPEED_WORLD",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.ips


    def expando(self):
        js='''
            function getExpando(){
                return "jQuery" + ('1.11.3' + Math.random()).replace(/\D/g, "")
            }
        '''
        expando_compile = execjs.compile(js)
        return expando_compile.call("getExpando")

    '''
        获取主页内容
    '''
    def main(self):
        try:
            self.headers["Host"] = "tool.chinaz.com"
            self.headers["Origin"] = "https://tool.chinaz.com"
            self.headers["Content-Type"] = "application/x-www-form-urlencoded"
            self.headers["Referer"] = "https://tool.chinaz.com/speedworld/%s"%(self.domain)
            self.headers["sec-ch-ua"] = '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"'
            self.headers["sec-ch-ua-mobile"] = "?0"
            self.headers["Sec-Fetch-Dest"] = "document"
            self.headers["Sec-Fetch-Mode"] = "navigate"
            self.headers["Sec-Fetch-Site"] = "same-origin"
            self.headers["Sec-Fetch-User"] = "?1"
            self.headers[
                "Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
            self.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
            url = self.main_url%(self.domain)
            self.marmo_log["datas"].append("speed world url =="+str(url))
            main_res = requests.get(url,headers=self.headers)
            if main_res.status_code ==200:
                html = main_res.text
                self.getSpeedList(html)
        except Exception as e:
            print("main 函数出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("main 函数出现异常==="+str(e.__str__()))



    '''
        从主页获取key
    '''
    def getKey(self,result):
        try:
            pattern ='<input type="hidden" id="enkey" value="(.*?)" />'
            key_res = re.findall(pattern,result,re.S)
            if key_res and len(key_res) >=1:
                return key_res[0]
            else:
                return ""
        except Exception as e:
            print("获取key出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("获取key出现异常==="+str(e.__str__()))
            return  ""

    '''
        获取speed_list
    '''
    def getSpeedList(self,result):
            try:
                encode = self.getKey(result)
                self.marmo_log["datas"].append("spped list encode =="+str(encode))
                speedSelector=Selector(text=result)
                divs = speedSelector.xpath('//div[@class="row listw clearfix"]/@id').extract()
                for id in divs:
                    '''
                        多地ping
                    '''
                    ip =self.ajax(id,encode)
                    if ip:
                        self.marmo_log["datas"].append("ip ==" + str(ip))
                        self.ips.append(ip)
            except Exception as e:
                print("获取speed list出现异常===="+str(e.__str__()))
                self.marmo_log["exceptions"].append("获取speed list出现异常===="+str(e.__str__()))
                return ""


    '''
        ajax请求 ping
    '''
    def ajax(self,guid,encode):
        try:
            callback = str(self.expando())+"_"+str(self.vb)
            url = self.query_url%(callback)
            self.marmo_log["datas"].append("speedworld ajax url =="+str(url))
            data ={
                "guid":guid,
                "host":self.domain,
                "ishost":"1",
                "isipv6":"undefined",
                "encode":encode,
                "checktype":"1"
            }
            self.marmo_log["datas"].append("ajax data =="+str(data))
            ajax_res = requests.post(url,headers=self.headers,data=data)
            if ajax_res.status_code ==200:
                ajax_text = ajax_res.text
                self.marmo_log["datas"].append("ajax text =="+str(ajax_text))
                return self.parse_ajax(ajax_text)
        except Exception as e:
            print(" ajax 出现异常===="+str(e.__str__()))
            self.marmo_log["exceptions"].append("ajax 出现异常===="+str(e.__str__()))
            return ""


    '''
        对ajax请求数据进行解析
    '''
    def parse_ajax(self,result):
        try:
            pattern="ip:'(.*?)',httpstate"
            ips = re.findall(pattern,result,re.S)
            self.marmo_log["datas"].append("parse ajax =="+str(ips))
            if ips and len(ips) >=1:
                return ips[0]
            return ""
        except Exception as e:
            print("parse ajax 出现异常===="+str(e.__str__()))
            self.marmo_log["exceptions"].append("parse ajax 出现异常===="+str(e.__str__()))
            return ""




if __name__ =="__main__":
    speedworld =SpeedWorld("mbap.abchina.com")
    speedworld.run()





