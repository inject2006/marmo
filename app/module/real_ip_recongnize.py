# -*- coding:UTF-8 -*-
'''
    真实ip判断模块
    第一步:查询出所有的cdn_ip,查询出所有的c段ip,如果cdn_ip在真实ip的c段上面,那么这个cdn_ip可能是真实的ip--->结果列表
    第二步:在censys网站进行ssl证书查询 ---结果集[ip1,ip2]
    第三步:fofa和shodan进行搜索
      fofa:[['www.nucc.com', '39.107.196.233', '80'], ['https://www.nucc.com', '39.107.196.233', '443'], ['https://im.nucc.com', '221.122.73.117', '443']]
      shodan:[ip1,ip2]
    第四步:站长之家进行国外多地ping
        speedworld.py,返回[ip1,ip2]
    第五步:F5 LTM解码法
    第六步:在线网站进行cname解析
        ipip_cdn.py   返回 [cdd0ocycuptgwwfkfbtcklx15sjnmxdj.yundunwaf4.com|未知|]

    第七步:ip138历史域名抓取


'''
# from .base import Base
from .cdn_module import Cdn
from .censys_api import CenSysApi
from .ipip_cdn import IpCname
from .shodan_api import ShoDan_Api
from .speedworld import SpeedWorld
from .fofa import FofaClient
from app.dao.online_asset_ip_dao import OnlineAssetIpDao
from app.dao.marmo_log_dao import MarmoLogDao
class RealIpRecongnize():
    '''
        必传参数{"project_id":""}
    '''
    def __init__(self,asset_data):
        self.asset_data = asset_data
        project_id = asset_data["project_id"]
        # self.domain=asset_data["domain"]
        # self.ip = asset_data["ip"]
        self.cdn_and_cduan_list =[]  #cdn和ip模块匹配的结果
        self.censys =[]
        self.network_engine ={}
        self.chinaz =[]
        self.f5 =[]
        self.cname =[]
        self.module_name = asset_data["module_name"]
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
        self.start_tag ="*"*10+"%s start "+"*"*10
        self.end_tag = "*" * 10 + "%s end " + "*" * 10



    '''
        获取138网站域名解析的结果
        current:当前解析结果
        history:历史解析结果
        
    '''
    def get138Explain(self,domain):
        history=Cdn({"domain":domain,"module_name":"real_ip","asset_id":self.asset_data["asset_id"],"asset_type":self.asset_data["asset_type"],"project_id":self.asset_data["project_id"],"project_name":self.asset_data["project_name"]}).getHistoryExplain()
        return history

    '''
        比对cdn和c段ip
        cdn_and_cduan_list就是cdn-ip和c段ip结合的结果
    '''
    def get_cdn_and_cduan(self,onlinedao):

        cdn_list,cduan_list = onlinedao.get_cduan_and_cdnIp({"project_name":self.asset_data["project_name"]})
        cdn_cduan_concat_list = [x for x in cdn_list if x in set(cduan_list)] #cdn-ip和c段ip比对的结果
        self.cdn_and_cduan_list=cdn_cduan_concat_list
        return cdn_list,cduan_list


    '''
        运行步骤:
        1.查找该项目下的所有cdnip和真实ip
        2.查找cdnip和对应的域名
        3.遍历cdn和域名
        4.ssl证书查询(域名)
        5.网络空间搜索引擎查询(域名)
        6.多地ping(域名)
        7.cname解析(域名)
        
    '''
    def run(self):
        try:
            onlinedao = OnlineAssetIpDao()
            '''
                需要project_name
            '''
            cdn_list,cduan_list =self.get_cdn_and_cduan(onlinedao)
            self.marmo_log["datas"].append("cdn list =="+str(cdn_list))
            self.marmo_log["datas"].append("cduan list =="+str(cduan_list))
            ip_domain_list =onlinedao.ip_related_domain(cdn_list)
            self.marmo_log["datas"].append("ip domain list =="+str(ip_domain_list))
            for ip_domain in ip_domain_list:
                log_info=""
                log_info += self.start_tag % ("table cdn ip and c_range ip")
                log_info += str(self.cdn_and_cduan_list)
                log_info += self.end_tag % ("table cdn ip and c_range ip")
                ip = ip_domain["ip"]
                domain = ip_domain["domain"]
                asset_id = ip_domain["id"]
                censys = CenSysApi({"domain":domain,"asset_id":asset_id})
                censys_ips =censys.run()
                log_info+=self.start_tag%("censys")
                log_info+=str(censys_ips)
                log_info+=self.end_tag%("censys")
                fofa = FofaClient({"domain":domain,"asset_id":asset_id})
                fofa_results =fofa.run()
                log_info += self.start_tag % ("fofa")
                log_info += str(fofa_results)
                log_info += self.end_tag % ("fofa")
                shodan = ShoDan_Api({"domain":domain,"asset_id":asset_id})
                shodan_result =shodan.run()
                log_info += self.start_tag % ("shodan")
                log_info += str(shodan_result)
                log_info += self.end_tag % ("shodan")
                speedworld = SpeedWorld({"domain":domain,"asset_id":asset_id})
                speed_result =speedworld.run()
                log_info += self.start_tag % ("speedworld")
                log_info += str(speed_result)
                log_info += self.end_tag % ("speedworld")
                cname = IpCname({"domain":domain,"asset_id":asset_id})
                result = cname.run()
                log_info += self.start_tag % ("cname")
                log_info += str(result)
                log_info += self.end_tag % ("cname")
                '''
                    获取138历史解析历史
                '''
                history =self.get138Explain(domain)
                log_info += self.start_tag % ("history")
                log_info += str(history)
                log_info += self.end_tag % ("history")
                '''
                    数据入库,这个状态跟域名关联
                '''
                self.data_info["exists_data"]=True
                self.data_info["status_code"]=2
                self.data_info["data"]=log_info
                self.marmo_log["datas"].append(log_info)



        except Exception as e:
            print("获取真实ip 出现异常===="+str(e.__str__()))
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
            self.data_info["fail_reason"]="获取真实ip 出现异常===="+str(e.__str__())
            self.marmo_log["exceptions"].append("获取真实ip 出现异常===="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": self.module_name,
                "type": '4',
                "module_log": str(self.marmo_log),
                "asset_id":int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info
if __name__ =="__main__":
    cdn = RealIpRecongnize({})
    cdn.run()









