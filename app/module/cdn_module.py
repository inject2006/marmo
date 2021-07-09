# -*- coding:UTF-8 -*-

'''
    138网站解析IP
    提供三个功能:
    1. 获取历史解析记录
    2.获取现在解析记录
    3.获取ip的位置和出口
'''
# from .base import Base
import math
import execjs
import re
import requests
import time
from scrapy.selector import Selector
from app.dao.asset_dao import AssetDao
from app.exceptions.module_exception import ModuleException
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
logger = Marmo_Logger()
class Cdn():
    def __init__(self,module_data={}):
        self.url ="https://site.ip138.com/%s/"
        self.currentUrl ="https://site.ip138.com/domain/read.do?domain=%s&time=%d"
        self.historyUrl="https://site.ip138.com/index/querybydomain/?domain=%s&page=%d&token=%s"
        self.write_url ="https://site.ip138.com/domain/write.do?type=domain&input=%s&token=%s"
        self.before_write_url="https://site.ip138.com/domain/write.do?input=%s&token=%s"
        self.report_url = "https://site.ip138.com/domain/write.do?type=domain&input=%s&token="
        self.domain =module_data["domain"]
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Host":"site.ip138.com",
            "sec-ch-ua":'" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "sec-ch-ua-mobile":'?0',
            "Sec-Fetch-Site":'same-origin',
            "Sec-Fetch-Mode":'cors',
            "Sec-Fetch-Dest":'empty',
            "Accept-Language":'zh-CN,zh;q=0.9'
        }
        '''
            当前解析记录
        '''
        self.current_set =set()
        '''
            历史解析记录
        '''
        self.history_set =set()
        self.current_count=5
        self.ip_location_url="https://www.ip138.com/iplookup.asp?ip=%s&action=2"
        self.module_data=module_data
        self.module_name=module_data["module_name"]
        self.data_info = {
            "exists_data": False,
            "status_code": 2,
            "fail_reason": "",
            "data": "",
            "module_name":self.module_name,
            "asset_type":module_data["asset_type"],
            "asset_id":module_data["asset_id"],
            "project_id":module_data["project_id"],
            "project_name":module_data["project_name"]
        }
        self.marmo_log ={
            "datas":[],
            "exceptions":[]
        }

    '''
        解析IP
    '''
    def getIP(self,value):
        numbers =[16777216,65536,256,1]
        arr =[]
        for number in numbers:
            arr.append(str(math.floor(value/number)))
            value = value%number
        return ".".join(arr)

    '''
        生成Hmt cookie
    '''
    def getHmt(self):
        js ='''
            function getAge(){
                return Math.round(+new Date / 1E3)
            }
        '''
        js_complie = execjs.compile(js)
        return js_complie.call('getAge')

    '''
        获取token
    '''
    def getToken(self,html):
        try:
            token_pattern="var _TOKEN = '(.*?)';"
            token_res = re.findall(token_pattern,html,re.S)
            self.marmo_log["datas"].append("token res =="+str(token_res))
            token =""
            if token_res and len(token_res) >=1:
                token =token_res[0]
            return token
        except Exception as e:
            print("获取token失败==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("获取token出现异常=="+str(e.__str__()))
            return ""

    '''
        获取首页内容
    '''
    def getIndexHtml(self):
        try:
            url = self.url%(self.domain)
            logger.log("cdn url =="+str(url))
            self.marmo_log["datas"].append("cdn url ==="+str(url))
            headers = self.headers
            headers["Referer"] = url
            index_res = requests.get(url, headers=headers)
            if index_res.status_code ==200:
                index_html = index_res.text

                self.token = self.getToken(index_html)
                logger.log("token==="+str(self.token))
                self.marmo_log["datas"].append("token =="+str(self.token))
                '''
                    请求write.do链接
                '''
                bak_url = self.before_write_url%(self.domain,self.token)
                logger.log("报备url=="+str(bak_url))
                self.marmo_log["datas"].append("报备url=="+str(bak_url))
                res = requests.get(bak_url,headers=headers)
                logger.log("报备状态码=="+str(res.status_code))
                self.marmo_log["datas"].append("报备状态码=="+str(res.status_code))
                if res.status_code ==200:
                    logger.log("报备请求体==="+str(res.text))
                self.parse_index_history(index_html)
                return index_html
            else:
                print("获取138网站主页状态码==="+str(index_res.status_code))
                raise Exception("获取138网站主页状态码==="+str(index_res.status_code))
        except Exception as e:
            print("获取138网站主页内容失败===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("获取138网站主页内容失败===" + str(e.__str__()))
            return ""

    '''
        获取部分历史解析记录
    '''
    def parse_index_history(self,result):
        try:

            history_selector=Selector(text=result)
            historys_ips = history_selector.xpath('//div[@id="J_ip_history"]/p/a/text()').extract()
            self.marmo_log["datas"].append("首页的当前历史解析ip=="+str(historys_ips))
            logger.log("首页的history数据==="+str(historys_ips))
            self.marmo_log["datas"].append("首页的history数据==="+str(historys_ips))
            for ip in historys_ips:
                self.history_set.add(ip)
        except Exception as e:
            print("parse_index_history 出现异常==="+str(e.__str__()))
            self.marmo_log["exceptions"].append("parse_index_history 出现异常==="+str(e.__str__()))


    '''
        获取当前时间戳
    '''
    def getTime(self):
        js ="function getDate(){return +new Date()}"
        time_complie = execjs.compile(js)
        return time_complie.call("getDate")

    '''
        获取当前解析IP
        https://site.ip138.com/domain/read.do?domain=mbap.abchina.com&time=1620484375901
        {"status":true,"code":300,"msg":"24f967dfea3eb39988dbb1f041d6b53720210508223256",
        "data":[{"ip":"219.147.109.13","sign":"d189cb0ce84fa18c97567d5070c8403f"}]}
        有五次机会，如果五次都没有返回结果，那么就没有结果
    '''
    def getCurrentExplain(self):
        try:
            self.getIndexHtml()
            count =1 #重试次数
            while count <self.current_count:
                currentTime = self.getTime() #获取当前时间戳
                url = self.currentUrl%(self.domain,currentTime)
                logger.log("current ajax url =="+str(url))
                self.marmo_log["datas"].append("current ajax url =="+str(url))
                headers = self.headers
                headers["Referer"] = self.url % (self.domain)
                current_res = requests.get(url, headers=headers)
                if current_res.status_code ==200:
                    current_text = current_res.json()
                    logger.log("当前解析结果==="+str(current_text))
                    self.marmo_log["datas"].append("获取当前解析结果="+str(current_text))
                    parse_result = self.parseCurrent(current_text)
                    if parse_result:
                        '''
                            请求write.do链接
                        '''
                        url = self.write_url%(self.domain,parse_result)
                        logger.log("write do url ==="+str(url))
                        self.marmo_log["datas"].append("write do url =="+str(url))
                        do_headers =self.headers
                        do_headers["Referer"]=self.url%(self.domain)
                        res = requests.get(url,headers =do_headers)
                        if res.status_code ==200:
                            logger.log("write.do 结果==="+str(res.text))
                            self.marmo_log["datas"].append("write.do 结果==="+str(res.text))
                        break
                    else:
                        time.sleep(1)
                        count+=1
                        continue
            self.marmo_log["datas"].append("请求过了5次")
            logger.log("请求过了5次")

            '''
                进行判断 domain_set >5?cdn:not_cdn，数据入库
            '''
            add_ip_params={
                "ip_type": 2,
                "location": "",
                "ip": "",
                "org": "",
                "source": 1,
                "source_detail":"" ,
                "description": "来自138网站对域名的当前解析",
                "is_belongs_to": 1,
                "project_id": int(self.module_data["project_id"]),
                "project_name":self.module_data["project_name"],
                "domain":self.domain,
                "celery_status":"5P"
            }

            is_cdn_ip=False
            exists_data=False

            if len(self.current_set) >=1:
                exists_data=True  #存在数据

            if len(self.current_set) >5:
                '''
                    cdn-ip
                '''
                is_cdn_ip=True #cdn-ip
                add_ip_params["ip_type"] = 2
            else:
                # 真实ip

                add_ip_params["ip_type"] =1
                is_cdn_ip=False
            if exists_data:
                self.data_info["exists_data"] = True
                self.data_info["data"] = str(self.current_set)
                assetdao =AssetDao()
                while len(self.current_set) >=1:
                    ip = self.current_set.pop()
                    add_ip_params["ip"]=ip
                    if is_cdn_ip:
                        add_ip_params["ip_type"] = 2
                    else:
                        add_ip_params["ip_type"] = 1
                    logger.log("新建ip参数=="+str(add_ip_params))
                    self.marmo_log["datas"].append("新增ip参数=="+str(add_ip_params))
                    assetdao.create_ip(add_ip_params)
            else:
                '''
                    没有数据
                '''
                self.data_info["exists_data"] = False

            return self.current_set
        except ModuleException as me:
            logger.log("模块功能当前解析列表出现异常"+str(me.__str__()))
            return ""
        except Exception as e:
            logger.log("获取当前解析IP内容失败===" + str(e.__str__()))
            return ""

    def report(self,token,referer):
        try:
            url = self.report_url%(self.domain,token)
            headers = self.headers
            headers["Referer"]=referer
            res = requests.get(url,headers=headers)
            if res.status_code ==200:
                print("上报结果==="+str(res.text))
        except Exception as e:
            print("report 出现异常=="+str(e.__str__()))
    '''
        获取历史IP
        {"status":false,"code":0,"msg":null}
        https://site.ip138.com/index/querybydomain/?domain=mbap.abchina.com&page=2&token=7a3d45d87e9684b0c22d911ea54d37c4
    '''
    def getHistoryExplain(self,):
        try:
            self.getIndexHtml()
            page=1
            while True:
                url = self.historyUrl%(self.domain,page,self.token)
                history_res = requests.get(url,headers=self.headers)
                if history_res.status_code ==200:
                    history_text = history_res.json()
                    self.marmo_log["datas"].append("获取历史解析记录="+str(history_text))
                    if history_text["status"] :
                        self.parseHistory(history_text)
                        page+=1
                    else:
                        self.marmo_log["datas"].append("没有历史解析记录")
                        break
                else:

                    break
            self.data_info["status_code"]=2
            if len(self.history_set) >=1:
                self.data_info["exists_data"]=True
                self.data_info["data"]=str(self.history_set)
        except Exception as e:
            logger.log("获取历史解析IP内容失败===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("获取历史解析IP内容失败===" + str(e.__str__()))

            # add_log_params = {
            #     "module": "CDN HISTORY",
            #     "type": '2',
            #     "module_log": str(self.marmo_log),
            #     "asset_id": int(self.module_data["asset_id"])
            # }
            # MarmoLogDao().add_log(add_log_params)
            self.data_info["status_code"]=3
            self.data_info["fail_reason"]="获取历史解析IP内容失败===" + str(e.__str__())
            self.data_info["exists_data"]=False
            # return self.data_info
        finally:
            '''
                入marmo_log表
            '''
            add_log_params = {
                "module": "REAL_IP_CDN_HISTORY",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.module_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info





    '''
        解析当前历史IP数据
    '''
    def parseCurrent(self,value):
        assert isinstance(value,dict)
        try:
            if value.__contains__("status"):
                status = value["status"]
                if status:
                    data = value["data"]
                    msg = value["msg"] or ""
                    for ip in data:
                        self.current_set.add(ip["ip"])
                    return msg
            else:
                return False
        except Exception as e:
            print("解析当前数据出现异常===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("解析当前数据出现异常=="+str(e.__str__()))
            return []

    '''
        获取历史IP
        {"status":true,"code":21000,"msg":"\u8fd4\u56de\u6210\u529f",
        "data":[{"_id":{"$id":"608b3f2bad2e260b1acbe288"},"ip":1956842889,"addtime":"20210430","uptime":"20210430"},
        {"_id":{"$id":"608b4057ad2e26661da07d8b"},"ip":1866283907,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d8c"},"ip":613849143,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d8d"},"ip":1991698090,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d8e"},"ip":2002038358,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d90"},"ip":28578342,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d91"},"ip":1956842885,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d92"},"ip":3079021125,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"608b4057ad2e26661da07d93"},"ip":3079021109,"addtime":"20210430","uptime":"20210430"},{"_id":{"$id":"5f9a002bad2e26a768b0b24e"},"ip":3054653578,"addtime":"20201029","uptime":"20210428"},{"_id":{"$id":"5f9a002bad2e26a768b0b255"},"ip":3054653584,"addtime":"20201029","uptime":"20210428"},{"_id":{"$id":"6010d60ead2e26982c5b56e7"},"ip":3079852035,"addtime":"20210127","uptime":"20210428"},{"_id":{"$id":"60121f5aad2e26b169922a5f"},"ip":3079852038,"addtime":"20210128","uptime":"20210428"},{"_id":{"$id":"6046db526ca2c84b0db7d00b"},"ip":3079852037,"addtime":"20210309","uptime":"20210428"},{"_id":{"$id":"60473597ad2e260672dd5c4a"},"ip":1017357844,"addtime":"20210309","uptime":"20210428"},{"_id":{"$id":"606db9c1ad2e262976cf42f7"},"ip":3079021106,"addtime":"20210407","uptime":"20210428"},{"_id":{"$id":"606db9c1ad2e262976cf42ee"},"ip":3079852043,"addtime":"20210407","uptime":"20210428"},{"_id":{"$id":"6072bcf4ad2e260242233ff3"},"ip":3079021101,"addtime":"20210411","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab02"},"ip":613849135,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab04"},"ip":2002038346,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab05"},"ip":1017357839,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab06"},"ip":3054653582,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab07"},"ip":1959758634,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab09"},"ip":1959758635,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab0b"},"ip":613849125,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab0c"},"ip":28578344,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab0f"},"ip":1991698089,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab10"},"ip":28578346,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab12"},"ip":613849127,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab13"},"ip":613849126,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab15"},"ip":3079021132,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab16"},"ip":2089065487,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab18"},"ip":613849145,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"60893483ad2e267c18f3ab1b"},"ip":28578348,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dca"},"ip":613849144,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dcb"},"ip":2089065489,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dcc"},"ip":1991698087,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dce"},"ip":3739014696,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dcf"},"ip":2002038349,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd1"},"ip":1866283910,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd2"},"ip":1959758628,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd3"},"ip":2089065483,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd5"},"ip":1991698086,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd7"},"ip":3079021096,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"608935afad2e26241cc18dd8"},"ip":2089065480,"addtime":"20210428","uptime":"20210428"},{"_id":{"$id":"601fa2bcad2e269535995c8a"},"ip":1786114441,"addtime":"20210207","uptime":"20210412"},{"_id":{"$id":"60399616ad2e268412772a99"},"ip":1881066313,"addtime":"20210227","uptime":"20210412"},{"_id":{"$id":"60399616ad2e268412772a9e"},"ip":1881066316,"addtime":"20210227","uptime":"20210412"},{"_id":{"$id":"604322a0ad2e26670c4f572a"},"ip":1881066319,"addtime":"20210306","uptime":"20210412"},{"_id":{"$id":"60473597ad2e260672dd5c4d"},"ip":1881066309,"addtime":"20210309","uptime":"20210412"}]}
    '''
    def parseHistory(self,value):
        assert isinstance(value, dict)
        try:
            if value.__contains__("status"):
                status = value["status"]
                if status:
                    if value.__contains__("data"):
                        data = value["data"]
                        for ip in data:
                            self.history_set.add(self.getIP(ip["ip"]))
        except Exception as e:
            print("解析历史数据出现异常===" + str(e.__str__()))
            self.marmo_log["exceptions"].append("解析历史数据出现异常==" + str(e.__str__()))
            return []
    '''
        运行函数
    '''
    def run(self):
        try:
            self.getCurrentExplain()
            logger.log(self.current_set)
            self.data_info["status_code"]=2
            self.data_info["exists_data"]=True
            if len(self.current_set) >=1:
                self.data_info["data"]=str(self.current_set)
                self.marmo_log["datas"].append("当前解析ip=="+str(self.current_set))

        except Exception as e:
            self.marmo_log["exceptions"].append("run 函数出现异常=="+str(e.__str__()))
            self.data_info["fail_reason"] = "run 函数出现异常==" + str(e.__str__())
            self.data_info["status_code"] = 3
            self.data_info["exists_data"]=False
        finally:
            add_log_params = {
                "module": "CDN",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.module_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)

            return self.data_info


if __name__ =="__main__":
    cdn = Cdn({"domain":"www.baidu.com","asset_id":1,"asset_type":1,"project_id":1,"project_name":"平安app","module_name":"cdn模块"})
    cdn.run()




