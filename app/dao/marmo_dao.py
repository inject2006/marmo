# -*- coding:UTF-8 -*-
'''
    数据库操作层
'''
from app.models import MarmoProject,ProcessInfoRelation,ProjectChargePerson,BaseSettings,ProcessInfo,User,Group
from app.utils.marmo_logger import Marmo_Logger
from django.db import connection
from marmo.settings import PER_PAGE
from datetime import datetime
from django_redis import get_redis_connection
import time
logger =Marmo_Logger()
class BaseSettingsDao():

    '''
        查询菜单
    '''
    def query_menu(self):
        menu_list =[]
        menus =BaseSettings.objects.filter(base_type=1).filter(is_available=1)
        all_menu = menus[:]
        print(all_menu)
        for menu in all_menu:
            menu_obj ={}
            menu_obj["name"]= menu.base_name
            menu_obj["menu_url"] = menu.base_value
            menu_list.append(menu_obj)
        return menu_list

    '''
        只查询个人中心
    '''
    @staticmethod
    def query_user_center():
        try:
            menu_obj ={}
            user_center_menu = BaseSettings.objects.filter(base_name="个人中心").get()
            if user_center_menu:
                menu_obj["name"]=user_center_menu.base_name
                menu_obj["menu_url"]=user_center_menu.base_value
                return menu_obj
        except Exception as e:
            logger.log("查询个人中心菜单出现异常==="+str(e.__str__))
            raise Exception("查询个人中心出现异常")

    def redis_init(self):
            redis_connection = get_redis_connection("default")
            base_value_list =[]
            base_values = BaseSettings.objects.filter(base_type=4,base_name="secrect")[:]
            if base_values:
                for base_obj in base_values:
                    base_value = base_obj.base_value
                    base_value_list.append(base_value)

            if base_value_list and len(base_value_list) >=1:
                '''
                    获取今年，然后设置十二个月的份额,比如2021-06
                '''
                year=time.strftime("%Y")
                months =["01","02","03","04","05","06","07","08","09","10","11","12"]
                for month in months:
                    redis_key = year+"-"+str(month)
                    is_exists = redis_connection.exists(redis_key)
                    if not is_exists: #如果key不存在
                        for base_value in base_value_list:
                            redis_connection.lpush(redis_key,base_value)


class UserDao():

    '''
        获取用户
    '''
    def get_user(self,account,password):
        try:
            if self.check_user_exists(account,password):
                user = User.objects.filter(account=account,password=password).get()
                return user
            else:
                logger.log("用户不存在")
                raise Exception("登录用户不存在")
        except Exception as e:
            raise Exception("登录用户不存在"+str(e.__str__()))
    '''
        用户id查询用户
    '''
    def query_user(self,user_id):
        try:
            user_obj ={}
            user= User.objects.get(id=user_id)
            if user:
                user_obj["name"]=user.nickname
                user_obj["avatar"]=user.avatar
            return user_obj
        except Exception as e:
            logger.log("查询用户出现异常==="+str(e.__str__()))
            raise Exception("用户不存在")

    '''
        查询全部用户
    '''
    def query_all_user(self):
        try:
            user_list = []
            users = User.objects.all()[:]
            for user in users:
                user_obj = {}
                user_obj["name"]=user.nickname
                user_obj["id"]=user.id
                user_list.append(user_obj)
            return user_list
        except Exception as e:
            logger.log("query all user exception ==="+str(e.__str__()))
            raise Exception("查询全部用户出现异常")

    '''
            查询个人渗透信息任务
        '''

    def query_user_process_info(self, user_id, page):
        assert page
        cursor = connection.cursor()
        try:
            page_start = (int(page) - 1) * PER_PAGE
            count_sql = "select count(1) from process_info p where p.responser=%d" % (int(user_id))
            sql = " select a.*,project.name from (select p.id,p.create_time,p.info_type,p.info_status,p.info_level,p.info_content,p.asset,p.user_id,p.project_id,p.responser,u.nickname from process_info p,`user` u  where  p.user_id =u.id and p.responser=%d) a left join marmo_project project on a.project_id=project.id limit %d,%d; " % (
            int(user_id), page_start, PER_PAGE)
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
                one_process["project_name"]=process_info[11]
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
                    history_string += str(create_time.strftime("%Y-%m-%d %H:%M:%S")) + "      "+str(sender)+"   -->" + str(nickname) + "\n\r"
                one_process["step"] = history_string
                user_process_list.append(one_process)
            return user_process_list, count
        except Exception as e:
            logger.log("查询用户任务出现异常==" + str(e.__str__()))
            raise Exception("查询用户任务出现异常")
        finally:
            if cursor:
                cursor.close()

    '''
        修改个人任务
        修改渗透任务
        负责人是否变更:是(添加流转记录),否:不用
        添加流水记录
        data:{"info_type":info_type,"info_user":info_user,"info_project":info_project,"info_status":info_status,
        "info_content":info_content,"process_info_id":process_info_id},

    '''

    def update_process_info(self, data):
        assert data["process_info_id"]
        assert data["info_type"]
        assert data["info_user"]
        assert data["info_status"]
        assert data["info_content"]
        assert data["info_project"]
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
                process_info.info_type = int(data["info_type"])
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
        检查用户是否存在
    '''
    def check_user_exists(self,account,password):
        try:
            user_exists = User.objects.filter(account=account,password=password).exists()
            if user_exists:
                return True
            else:
                return False
        except Exception as e:
            logger.log("检查用户出现异常==="+str(e.__str__()))
            raise Exception("检查用户出现异常==="+str(e.__str__()))







class ProjectDao():
    '''
        查询所有的项目
    '''
    def query_all_project(self):
        try:
            project_results =MarmoProject.objects.all()[:]
            project_list =[]
            for project in project_results:
                project_obj = {}
                project_obj["name"]=project.name
                project_obj["id"]=project.id
                project_obj["customer"]=project.customer
                project_obj["status"] = project.status
                project_obj["create_time"] = project.create_time.strftime("%Y-%m-%d %H:%M:%S")
                project_obj["delivery_date"]=project.delivery_date.strftime("%Y-%m-%d")
                project_obj["actual_delivery_date"]=project.actual_delivery_date.strftime("%Y-%m-%d")
                project_obj["work_time"]=project.work_time
                project_obj["pentest_tech"]=project.pentest_tech
                project_obj["summary"]=project.summary
                '''
                    查询项目的三个组成员
                '''
                info_user_id,tool_user_id,expert_user_id = self.query_three_group(project.id)
                project_obj["info_user_id"]=info_user_id
                project_obj["tool_user_id"] = tool_user_id
                project_obj["expert_user_id"] = expert_user_id
                project_list.append(project_obj)
            count = MarmoProject.objects.count()
            return project_list,count
        except Exception as e:
            logger.log("查询所有项目出现异常==="+str(e.__str__()))
            raise Exception("查询所有项目出现异常")

    '''
        创建项目
       data:{"project_name":project_name,"customer":customer,"info_group":info_group,"tool_group":tool_group,"expert_group":expert_group,
       "work_time":work_time,"pentest_tech":pentest_tech,"delivery_date":delivery_date,"actual_delivery_date":actual_delivery_date,
       "summary":summary,"status":project_status,"mode":current_mode}
    '''
    def get_dict_data(self,data,keyword):
        assert isinstance(data,dict)
        if data.__contains__(keyword):
            result = data[keyword]
            return result or "";
        else:
            return ""

    '''
        根据项目id查询三个组成员
    '''
    def query_three_group(self,project_id):
        try:
            '''
                查询出三个组id
            '''
            print("项目id==="+str(project_id))
            info_group = Group.objects.filter(group_name='信息组').get()
            tool_group = Group.objects.filter(group_name='工具组').get()
            expert_group = Group.objects.filter(group_name='专家组').get()
            if info_group and tool_group and expert_group:
                info_group_id = info_group.id
                tool_group_id = tool_group.id
                expert_group_id = expert_group.id
                info_user_id=''
                tool_user_id=''
                expert_user_id=''
                groups = ProjectChargePerson.objects.filter(project_id=project_id).all()[:]
                if groups:
                    for group in groups:
                        group_id = group.group_id
                        user_id = group.user_id
                        if group_id ==info_group_id:
                            info_user_id=user_id
                        elif group_id ==tool_group_id:
                            tool_user_id = user_id
                        elif group_id ==expert_group_id:
                            expert_user_id=user_id
                    return info_user_id,tool_user_id,expert_user_id
                else:
                    logger.log("查询项目组负责人出现异常"+str(groups))
                    raise Exception("查询项目组负责人出现异常")
            else:
                logger.log("查询组出现异常")
                raise Exception("查询组出现异常")
        except Exception as e:
            raise Exception("query_three_group 出现异常=="+str(e.__str__()))


    def create_project(self,data):
        try:
            '''
                查找出三个组的id
            '''
            info_group = Group.objects.filter(group_name='信息组').get()
            tool_group = Group.objects.filter(group_name='工具组').get()
            expert_group =Group.objects.filter(group_name='专家组').get()
            if info_group and tool_group and expert_group:
                info_user_id = info_group.id
                tool_user_id = tool_group.id
                expert_user_id =expert_group.id
                '''
                    获取自增数据的id,默认创建的项目状态是未开始
                '''
                obj ={"name":self.get_dict_data(data,"name"),"customer":self.get_dict_data(data,"customer"),"comments":"","status":0,"delivery_date":self.get_dict_data(data,"delivery_date"),"actual_delivery_date":self.get_dict_data(data,"actual_delivery_date"),
                      "assets_scope":"","work_time":self.get_dict_data(data,"work_time"),"pentest_level":"","pentest_tech":self.get_dict_data(data,"pentest_tech"),"summary":self.get_dict_data(data,"summary")}
                project_obj =MarmoProject.objects.create(**obj)
                project_id = project_obj.id
                '''
                    创建项目的三个组
                '''
                infogroup =ProjectChargePerson(group_id=info_user_id,user_id=data["info_user_id"],project_id=project_id)
                infogroup.save()
                toolgroup = ProjectChargePerson(group_id=tool_user_id, user_id=data["tool_user_id"], project_id=project_id)
                toolgroup.save()
                expertgroup = ProjectChargePerson(group_id=expert_user_id, user_id=data["expert_user_id"], project_id=project_id)
                expertgroup.save()
                return True
            else:
                logger.log("三个组还没有创建，请先创建工具组,专家组,信息组")
                return False
        except Exception as e:
            logger.log("创建项目出现异常==="+str(e.__str__()))
            raise Exception("创建项目出现异常")

    '''
        修改项目
        查找项目相关联的三个组
        判断组负责人是否变更-->更新
        项目参数变更--保存
    '''
    def update_marmo_project(self,data):
        try:
            project_name = data["name"]
            if project_name:
                project_obj = MarmoProject.objects.filter(name=project_name).get()
                if project_obj:
                    project_id = project_obj.id
                    info_group = Group.objects.filter(group_name='信息组').get()
                    tool_group = Group.objects.filter(group_name='工具组').get()
                    expert_group = Group.objects.filter(group_name='专家组').get()
                    if info_group and tool_group and expert_group:
                        info_user_id = info_group.id
                        tool_user_id = tool_group.id
                        expert_user_id = expert_group.id
                        '''
                            查询项目对应的三个组的成员
                        '''
                        groups = ProjectChargePerson.objects.filter(project_id=project_id).all()[:]
                        if groups:
                            for group in groups:
                                group_id = group.group_id
                                user_id =group.user_id
                                if group_id ==info_user_id: #信息组
                                    if user_id !=int(data["info_user_id"]):
                                        '''
                                            信息组成员有变更
                                        '''
                                        info_project_charge_person = ProjectChargePerson.objects.filter(user_id=user_id).get()
                                        info_project_charge_person.user_id =int(data["info_user_id"])
                                        info_project_charge_person.save()
                                elif group_id ==tool_user_id: #工具组
                                        if user_id != int(data["tool_user_id"]):
                                            '''
                                                信息组成员有变更
                                            '''
                                            tool_project_charge_person = ProjectChargePerson.objects.filter(user_id=user_id).get()
                                            tool_project_charge_person.user_id = int(data["tool_user_id"])
                                            tool_project_charge_person.save()
                                elif group_id ==expert_user_id: #专家组
                                        if user_id != int(data["expert_user_id"]):
                                            '''
                                                信息组成员有变更
                                            '''
                                            expert_project_charge_person = ProjectChargePerson.objects.filter(user_id=user_id).get()
                                            expert_project_charge_person.user_id = int(data["expert_user_id"])
                                            expert_project_charge_person.save()

                                '''
                                    修改项目
                                '''
                                project_obj = MarmoProject.objects.filter(id=project_id).get()
                                if project_obj:
                                    if data.__contains__("customer"):
                                        project_obj.customer = data["customer"]
                                    if data.__contains__("name"):
                                        project_obj.name = data["name"]
                                    if data.__contains__("delivery_date"):
                                        project_obj.delivery_date = datetime.strptime(data["delivery_date"], "%Y-%m-%d").date()
                                    if data.__contains__("actual_delivery_date"):
                                        project_obj.actual_delivery_date =datetime.strptime(data["actual_delivery_date"], "%Y-%m-%d").date()
                                    if data.__contains__("work_time"):
                                        project_obj.work_time =data["work_time"]
                                    if data.__contains__("pentest_tech"):
                                        project_obj.pentest_tech = data["pentest_tech"]
                                    if data.__contains__("summary"):
                                        '''
                                            有复盘总结前提是项目已经结束
                                        '''
                                        if project_obj.status ==2 or project_obj.status =="2":
                                            project_obj.summary = data["summary"]
                                    if data.__contains__("status"):
                                        project_obj.status = data["status"]
                                    project_obj.create_time =datetime.strptime(project_obj.create_time.strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                                    project_obj.update_time = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                                    project_obj.save()
                                    return  True
                                else:
                                    logger.log("项目不存在")
                                    raise Exception("项目不存在")
                        else:
                            logger.log("项目指定的信息组,工具组,专家组未指定")
                            raise Exception("项目指定的信息组,工具组,专家组未指定")
                    else:
                        logger.log("请先创建三个组")
                        raise Exception("请先创建三个组")
        except Exception as e:
            logger.log("修改项目出现异常==="+str(e.__str__()))
            raise Exception("修改项目出现异常"+str(e.__str__()))


    '''
        根据项目名称查询id
    '''
    def query_project_id_by_name(self,project_name):
        try:
            assert project_name
            project_obj = MarmoProject.objects.filter(name=project_name).get()
            if project_obj:
                return project_obj.id
            else:
                raise Exception("项目名称不存在")
        except MarmoProject.DoesNotExist:
            print("项目不存在")
        except Exception as e:
            print("查询项目出现异常=="+str(e.__str__()))
            return False







                










