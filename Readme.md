#0703提交修改内容
 1.修复资产管理页面搜索框输入c段ip不起作用
 2.修复资产管理页面每进一页数据累积的问题
 3.增加redis数据初始化接口
4.修改开放接口页面web资产查询问题
5.module目录下的各组件日志更加详细,固定的一些常量定义在settings文件
6.目录爆破方式改成dirsearch
7.前端页面log_info弹框样式修改
8.前端用户中心重复添加问题修复

每个模块返回数据格式/队列里面放置的数据
{
    exists_data:模块执行完后是否有数据
    ,status_code:状态码2/3
    data:返回的字符串数据
    fail_reason:错误日志,
    module_name:模块名称
    asset_type:资产类型
    asset_id:资产id
    project_id:项目id
    project_name
}
版本:1.0.0
使用命令:
    进入项目目录:cd /data/marmo
    #python3 -m venv env
    启动虚拟环境:source /data/marmo/env/bin/activate  进入虚拟环境
    #deactivate  离开虚拟环境
   启动命令:python3 manage.py runserver 0.0.0.0:8080
   worker启动命令:cd /data/marmo && celery -A marmo worker --loglevel=info
   启动后台任务:cd /data/marmo && python3 manage.py process_tasks
    启动监控:celery -A marmo flower --port=5555 --broker=redis://:deruiA321@192.168.0.48:6379/13

###项目目录介绍:
marmo:项目根目录
  app:app应用目录
     dao:数据库操作文件包
     exceptions:自定义异常包
     middleware:中间件包
     migrations:数据库迁移记录
     module:模块功能包
     utils:工具包
     __init__.py:文件
     admin.py:
     apps.py:
     config.py:
     models.py:模型定义文件
     tasks.py:任务定义文件
     test.py:
     views.py:
     worker.py:定时任务文件

  marmo:django生成的自带目录
    __init__.py:
    asgi.py:
    celery.py:异步任务文件
    settings.py:配置文件
    urls.py:路由文件
    wsgi.py:
  media:图片文件目录
  pd:数据库文件目录
  static:静态资源目录
    css:样式目录
    font:字体目录
    js:脚本目录

  templates:模板目录
  venv:虚拟环境目录
  __init__.py:初始化文件
  db.sqlite3:sqlite数据库
  manage.py:自带文件
  modify_0519.sql:备份sql文件
  Readme.md:说明文件
  requirements.txt:依赖库

目前尚存在的bug：
    1.goBuster爆破进度慢

安装chrome
vi /etc/yum.repos.d/google-chrome.repo
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub

yum install google-chrome-stable -y

安装控件:
安装pip2  :python2 pip-get.py
go安装:
wget https://golang.google.cn/dl/go1.16.5.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.16.5.linux-amd64.tar.gz
vi /etc/profile
export GOROOT=/usr/local/go
export GOPATH=/usr/local/gopath
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
source /etc/profile

安装gobuster:
  pass

whois安装:yum install whois -y

nmap 安装: yum install namp -y
rustscan安装:
yum install epel-release
yum install dnf
dnf copr enable atim/rustscan -y
dnf install rustscan -y
安装masscan：
  yum install git gcc libpcap* -y
  git clone https://github.com/robertdavidgraham/masscan
  cd masscan
  make && make install


###外部环境安装
pip2 install requests
pip2 install gevent
pip2 install bs4
pip2 install lxml




0705更新，版本1.0.1
增加修改安全设备时设备和所属公司不能改变
端口页面目录爆破弹框的url经过decodeURLcompoment

0706:
问题1:
    发现celery下的依赖组件的一个问题:
    Cannot route message for exchange 'reply.celery.pidbox': Table empty or key no longer exists
    原因:kobumu版本为5.1.0,经网上查询，这是组件的bug,需要减低版本到4.6.4,待验证
问题2：
    missed heartbeat from celery
    celery心跳失常，启动时添加参数--without-heartbeat

问题3:
    Substantial drift from celery@node6 may mean clocks are out of sync
    原因:各个服务器之间的时间不同步,使用ntpdate同步时间





  

