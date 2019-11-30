"""autoserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from web import views
urlpatterns = [
    #首页
    url(r'^index/$',views.index,name="index"),

    # #主机
    #     #展示
    # url(r'^server_list/$',views.Server_list,name="server_list"),
    #     #新增
    # url(r'^server_add/$',views.Server_change,name="server_add"),
    #     #编辑
    # url(r'^server_edit/(\d+)/$', views.Server_change, name='server_edit'),
    # 主机详情展示
    # url(r'^server_detail/(\d+)/$', views.Server_detail, name='server_detail'),
    # # 主机变更记录展示
    # url(r'^server_record/(\d+)/$', views.Server_record, name='server_record'),
]
