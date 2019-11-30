from stark.service.stark import site, StarkConfig, get_choice_text, Option

from repository import models
from django.shortcuts import HttpResponse, render
from django.utils.safestring import mark_safe
from django.urls import reverse

from django.conf.urls import url
from stark.service.stark import site,StarkConfig
from repository import models

class BusinessUnitConfig(StarkConfig):
    # 展示的字段 列表中使用数据表的字段名
    list_display = [StarkConfig.display_checkbox,'id', 'name']
    # 排序
    order_by = ['-id']
    # 搜索
    search_list = ['name']
    # 批量操作

    def mutli_delete(self, request):
        print(request.POST)
        return HttpResponse('删除成功')

    mutli_delete.text = '批量删除111'
    ####下拉框 列表中mutli_delete对应上面的mutli_delete  为了区分功能
    action_list = [mutli_delete]
#models.BusinessUnit 对哪个表做操作
#使用BusinessUnitConfig这个类
site.register(models.BusinessUnit, BusinessUnitConfig)
class IDCConfig(StarkConfig):
    '''
    IDC管理
    '''
    # 展示的字段
    list_display = ['id', 'name', 'floor']
    # 排序
    order_by = ['-id']
    # 搜索
    search_list = ['name', 'floor']
site.register(models.IDC,IDCConfig)

class IDCConfig(StarkConfig):
    '''
    IDC管理
    '''
    # 展示的字段
    list_display = ['id', 'name', 'floor']
    # 排序
    order_by = ['-id']
    # 搜索
    search_list = ['name', 'floor']
site.register(models.IDC,IDCConfig)

from stark.forms.forms import StarkModelForm
from stark.forms.widgets import DatePickerInput

class ServerForm(StarkModelForm):
    class Meta:
        model = models.Server
        fields = '__all__'
        #class':'date-picker' 样式
        #'autocomplete':'off'  去掉input框内的历史搜索记录
        widgets = {
            'latest_date':DatePickerInput(attrs={'class':'date-picker','autocomplete':'off'})
        }



class ServerConfig(StarkConfig):
    '''
        主机管理
        '''
    #使用ServerForm
    model_form_class = ServerForm
    def show_satus(self, header=None, row=None):
        if header:
            # 表头（页面展示使用）
            return '设备状态'
        #print(row)  c4.com   这里的c4.com不是主机名，是当前server的对象，之所以打印主机名是因为表内定义了__str__方法
        # mark_safe 将代码在页面生效
        # get_device_status_id_display()  取choices值
        if row.get_device_status_id_display()=="上架":
            ret='<span style="color:sienna">{}</span>'.format(row.get_device_status_id_display())
        elif row.get_device_status_id_display()=="在线":
            ret = '<span style="color:green">{}</span>'.format(row.get_device_status_id_display())
        elif row.get_device_status_id_display()=="离线":
            ret = '<span style="color:red">{}</span>'.format(row.get_device_status_id_display())
        return mark_safe(ret)
    def show_hostname(self, header=None, row=None):
        if header:
            return '主机名'
        return mark_safe('<a href="{}"> {} </a>'.format('/stark/repository/server/server_detail/{}'.format(row.pk), row.hostname))

    def show_record(self, header=None, row=None):
        if header:
            return '变更记录'
        return mark_safe(
            '<a href="{}"> <i class="fa fa-outdent"> 查看</i> </a>'.format('/stark/repository/server/server_record/{}/'.format(row.pk), ))
    # 展示的字段
    list_display = [StarkConfig.display_checkbox,'id', show_hostname, 'idc', 'cabinet_num', 'cabinet_order', show_record,show_satus,'latest_date']
    # 排序
    order_by = ['id']
    # 搜索
    search_list = ['hostname']

    # 批量操作

    def mutli_delete(self, request):
        print(request.POST)
        return HttpResponse('删除成功')

    mutli_delete.text = '批量删除'
    ####下拉框 列表中mutli_delete对应上面的mutli_delete  为了区分功能
    action_list = [mutli_delete]

    def server_detail(self, request, pk):
        obj = models.Server.objects.filter(pk=pk).first()
        disks = obj.disk_list.order_by('slot')
        return render(request, 'server_detail.html', {'obj': obj, 'disks': disks})

    def server_record(self, request, pk):
        obj = models.Server.objects.filter(pk=pk).first()
        return render(request, 'server_record.html', {'obj': obj})

    def extra_url(self):
        urlpatterns = [

            url(r'^server_detail/(\d+)/$', self.server_detail, name='server_detail'),
            url(r'^server_record/(\d+)/$', self.server_record, name='server_record'),
        ]
        return urlpatterns

    # 组合搜索  组合筛选
    #按照字段搜索
    #is_multi=True 多选
    #condition={'pk__in': [1,3,5,]}  如果展示过多，使用此方法筛选展示搜索条件，这里代表展示pk为1,3,5的对象
    #is_choice=True  如果字段是choice,要加上这个参数
    #text_func=lambda x: x[1]   自定义显示内容  比如 （1,"上架"）  text_func=lambda x: x[1] 后只显示 上架  看着美观
    list_filter = [
        Option('idc', is_multi=True, condition={'pk__in': [1,2,3,4,5, ]}),
        # Option('business_unit'),
        Option('device_status_id', is_choice=True, text_func=lambda x: x[1])
    ]



site.register(models.Server, ServerConfig)