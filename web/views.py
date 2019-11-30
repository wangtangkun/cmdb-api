from django.shortcuts import render,HttpResponse,redirect
from repository import models
from web.form import ServerForm


# Create your views here.


def index(request):
    return render(request, 'index.html')
#
# def Server_list(request):
#     '''
#     展示Server(主机)
#     :param request:
#     :return:
#     '''
#     server=models.Server.objects.all()
#     return render(request,"server_list.html",{"server":server})
#
# def Server_change(request,pk=None):
#     '''
#     新增 修改主机
#     :param request:
#     :return:
#     '''
#     #查询修改的对象（新增为空）
#     obj=models.Server.objects.filter(pk=pk).first()
#     #将对象传入ServerForm中（新增为空），所以 编辑页面带有现在的数据， 新增页面字段都是空
#     form_obj = ServerForm(instance=obj)
#     if request.method=="POST":
#         #request.POST 本次提交数据    instance=obj 数据库中数据   传入ServerForm
#         form_obj=ServerForm(request.POST,instance=obj)
#         if form_obj.is_valid():
#             form_obj.save()
#             return redirect('web:server_list')
#     return render(request, 'form.html', {'form_obj': form_obj})
#
# def Server_detail(request,pk):
#     '''
#     主机详情页面
#     :param request:
#     :return:
#     '''
#     obj=models.Server.objects.filter(pk=pk).first()
#     return render(request,"server_detail.html",{"obj":obj})
#
# def Server_record(request,pk):
#     obj = models.Server.objects.filter(pk=pk).first()
#     return render(request, "server_record.html", {"obj": obj})