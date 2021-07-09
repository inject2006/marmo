# -*- coding:UTF-8 -*-
'''
    渗透信息任务
'''
from app.models import ProcessInfo,ProcessInfoRelation,MarmoProject
from app.utils.marmo_logger import Marmo_Logger
from django.db import connection
from datetime import datetime
PER_PAGE=100
logger = Marmo_Logger()
class ProcessInfoDao():
    '''
        新增渗透信息
        input:
        info_level:信息重要性
        info_content:渗透内容
        user_id:创建人
        responser:关联人/负责人
        asset:关联资产

    '''
    def create_process_info(self,data):
        try:
            project_name= data["project_name"]
            if project_name:
              project_obj = self.query_project_exists_by_name(project_name)
              if project_obj:
                create_process_info_obj ={
                    "info_type":1,
                    "info_status":1,
                    "info_level":int(data["info_level"]),
                    "info_content":data["info_content"],
                    "user_id":int(data["user_id"]),
                    "responser":int(data["responser"]),
                    "project_id":int(project_obj.id),
                    "asset":data["asset"]
                }
                process_info = ProcessInfo.objects.create(**create_process_info_obj)
                if process_info:
                    '''
                        创建一个关系
                    '''
                    process_info_relation = ProcessInfoRelation(receiver=create_process_info_obj["responser"],process_info_id=process_info.id,sender=create_process_info_obj["user_id"])
                    process_info_relation.save()
                    return True
                else:
                    return False
        except Exception as e:
            logger.log("创建渗透任务失败=="+str(e.__str__()))
            raise Exception("创建渗透任务失败"+str(e.__str__()))

    '''
        查询项目的渗透信息
    '''

    def query_process_info(self, data):
        cursor = connection.cursor()
        try:
            page = data["page"]
            limit = data["limit"] or 10
            project_name = data["project_name"]
            asset = data["asset"]
            if project_name:
                project_obj = self.query_project_exists_by_name(project_name)
                if project_obj:
                    project_id = project_obj.id
                    page_start = (int(page) - 1) * int(limit)
                    count_sql = "select count(1) from process_info p where p.project_id=%d" % (int(project_id))
                    sql = " select p.id,p.create_time,p.info_type,p.info_status,p.info_level,p.info_content,p.asset,p.user_id,p.project_id,p.responser,u.nickname from process_info p,`user` u  where  p.user_id =u.id and p.asset='%s'and p.project_id=%d limit %d,%d; " % (
                    asset,int(project_id), page_start, int(limit))
                    print(sql)
                    cursor.execute(sql)
                    process_info_results = cursor.fetchall()
                    print(process_info_results)
                    cursor.execute(count_sql)
                    count = cursor.fetchone()[0]
                    '''
                        遍历用户全部渗透任务
                    '''
                    user_process_list = []
                    for process_info in process_info_results:
                        one_process = {}
                        one_process["id"] = process_info[0]
                        one_process["create_time"] = process_info[1]
                        one_process["create_user"] = process_info[10]
                        one_process["info_content"] = process_info[5]
                        one_process["info_level"] = process_info[4]
                        one_process["info_status"] = process_info[3]
                        one_process["info_type"] = process_info[2]
                        one_process["asset"] = process_info[6]
                        one_process["project_id"] = process_info[8]
                        one_process["responser"] = process_info[9]
                        process_info_id = process_info[0]
                        '''
                            查询任务的流转历史
                        '''
                        process_info_history_sql = "select a.create_time,a.nickname as receiver,u2.nickname as sender from (select p.create_time,u.nickname,p.sender from process_info_relation p,user u where p.receiver=u.id and p.process_info_id=%d) a left join user u2 on a.sender =u2.id;" % (
                    int(process_info_id))
                        cursor.execute(process_info_history_sql)
                        process_history_list = cursor.fetchall()
                        history_string = ""
                        for history in process_history_list:
                            create_time = history[0]
                            nickname = history[1]
                            sender = history[2]
                            history_string +=str(create_time.strftime("%Y-%m-%d %H:%M:%S")) + "      "+str(sender)+"   -->" + str(nickname) + "\n\r"
                        one_process["step"] = history_string
                        user_process_list.append(one_process)
                    return user_process_list, count
                raise Exception("查询渗透信息项目参数异常")
            raise Exception("查询渗透信息项目参数异常")
        except Exception as e:
            logger.log("查询用户任务出现异常==" + str(e.__str__()))
            raise Exception("查询用户任务出现异常")
        finally:
            if cursor:
                cursor.close()

    '''
        修改渗透任务
        负责人是否变更:是(添加流转记录),否:不用
        添加流水记录
        data:{"info_type":info_type,"info_user":info_user,"info_project":info_project,"info_status":info_status,
        "info_content":info_content,"process_info_id":process_info_id},

    '''

    def update_process_info(self, data):
        try:
            print(data)
            process_info = ProcessInfo.objects.filter(id=data["process_info_id"]).get()
            if process_info:
                responser = process_info.responser
                if responser != int(data["info_user"]):
                    '''
                        负责人变更,需要添加流转记录
                    '''
                    pr = ProcessInfoRelation(receiver=data["info_user"], process_info_id=data["process_info_id"],
                                             sender=responser, create_time=datetime.now(), update_time=datetime.now())
                    pr.save()
                    process_info.responser = int(data["info_user"])
                if data.__contains__("info_type"):
                    process_info.info_type = int(data["info_type"])
                if data.__contains__("info_project"):
                    process_info.info_project = int(data["info_project"])
                process_info.info_status = int(data["info_status"])
                process_info.info_content = data["info_content"]
                process_info.save()
                return True
        except ProcessInfo.DoesNotExist:
            logger.log("渗透任务不存在")
            raise Exception("渗透任务不存在")
        except Exception as e:
            logger.log("修改渗透任务异常===" + str(e.__str__()))
            raise Exception("修改渗透任务异常")

    '''
            根据项目名称查询项目是否存在
        '''

    def query_project_exists_by_name(self, project_name):
        assert project_name
        try:
            project_obj = MarmoProject.objects.filter(name=project_name).get()
            return project_obj
        except MarmoProject.DoesNotExist:
            logger.log("新增域名项目不存在")
            raise Exception("新增域名项目不存在")
        except Exception as e:
            logger.log("query project exists " + str(e.__str__()))
            raise Exception("query project exists " + str(e.__str__()))




