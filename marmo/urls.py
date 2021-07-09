"""marmo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.static import serve
from marmo import settings
from app.views import IndexView,ProjectView,UserView,VulnView,ProcessInfoView,AssetView,LoginView,DomainView,IPView,SecurityView,LogInfoView,ServiceView,WebrecongnizeView,SideStationsView,RunView,TaskView,TestView,LogoutView,DirbusterView,RedisInitView
from app.views import MenuJson
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',IndexView.as_view(),name="index"),
    path("",LoginView.as_view(),name="default_index"),
    url(r'^media/(?P<path>.*)$',serve,{"document_root":settings.MEDIA_ROOT},name="media"),
    path('project/',ProjectView.as_view(),name="project"),
    path('user/',UserView.as_view(),name="user"),
    path('vuln/',VulnView.as_view(),name="vuln"),
    path('asset/',AssetView.as_view(),name="asset"),
    path('process/',ProcessInfoView.as_view(),name="process"),
    path('menujson/',MenuJson.as_view(),name="menujson"),
    path('login/',LoginView.as_view(),name="login"),
    path('domain/',DomainView.as_view(),name="domain_add_update"),
    path('ip/',IPView.as_view(),name="ip_add_update"),
    path('security/',SecurityView.as_view(),name="security_add_update"),
    path('loginfo/',LogInfoView.as_view(),name="loginfo"),
    path('service/',ServiceView.as_view(),name="service"),
    path('recongnize/',WebrecongnizeView.as_view(),name="recongnize"),
    path('sidestations/',SideStationsView.as_view(),name="sidestations"),
    path('run/',RunView.as_view(),name="run"),
    path('background_tasks/',TaskView.as_view(),name="tasks"),
    path('test/',TestView.as_view(),name="test"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('dirbuster/',DirbusterView.as_view(),name="dirbuster"),
    path('redisinit/',RedisInitView.as_view(),name="redisinit")
    # url(r'^static/(?P<path>.*)$', serve,
    #     {'document_root': settings.STATIC_ROOT}, name='static'),

]
