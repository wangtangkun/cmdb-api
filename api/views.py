from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models
from .service import process_basic, process_disk, process_memory, process_nic
from django.http import HttpResponse,JsonResponse
KEY = 'wangtangkun'
import hashlib
import time
def gen_key(ctime):
    key = "{}|{}".format(KEY, ctime)

    md5 = hashlib.md5()
    md5.update(key.encode('utf-8'))

    return md5.hexdigest()

class AuthView(APIView):

    def dispatch(self, request, *args, **kwargs):

        if request.method != 'POST':
            return super().dispatch(request, *args, **kwargs)

        ret = {'stauts': True, 'msg': 'ok'}

        client_key = request.GET.get('key')
        now = time.time()

        ctime = request.GET.get('ctime',now)

        server_key = gen_key(ctime,)


        if now - float(ctime) > 2:
            # 时间超时
            ret['stauts'] = False
            ret['msg'] = '来的有点晚了'
            return JsonResponse(ret)

        if client_key != server_key:
            ret['stauts'] = False
            ret['msg'] = '验证不通过'
            return JsonResponse(ret)

        else:

            return super().dispatch(request, *args, **kwargs)
class Asset(AuthView):
    def get(self, request):
        '''
        处理获取数据请求
            向ssh 或salt 模式的中控机，发送需要被执行命令的主机名或ip
        :param request:
        :return:
        '''
        host_list = ['192.168.179.131', '192.168.179.130']

        #自动序列化  发送数据
        return Response(host_list)


    def post(self, request):

        # 自动反序列化  接收数据  依据发送端的 headers={'content-type': 'application/json'}
        print(request.data)


        info = request.data

        #获取接收到的数据(字典) 中的action字段(操作信息)
        action = info.get('action')

        #从接收的数据中，查到主机名
        hostname = info['basic']['data']['hostname']

        #定义一个字典，包含响应状态和主机名
        result = {
            'status':True,
            'hostname' : hostname
        }
        print(info)
        print(action)
        print("result",result)

        #根据操作信息，作具体操作
        if action == 'create':
            # 新增资产信息
            print('新增资产信息')
        ###新增Server
            #定义一个字典，存放数据
            server_info = {}
            #根据数据，生成三个字典
            basic = info['basic']['data']
                #info字典数据格式 看 脚本/info.py
                #举例取basic段数据，查看格式：
            # 规律: data字典(具体数据) 中  key和数据表字段名相同,所以将需要写入数据库中的数据,加入到一个字典中，打散插入即可：
                    #basic
                    #':{
                    # 'status':True,
                    # 'error':'',
                    # 'data':{
                    # 'os_platform':'linux',
                    # 'os_version':'6.5',
                    # 'hostname':'c1.com'
                    # }
                    # },
                        #数据表中字段：
                            # 基本信息 + 主板信息 + CPU信息
                            # hostname = models.CharField('主机名', max_length=128, unique=True)
                            # os_platform = models.CharField('系统', max_length=16, null=True, blank=True)
                            # os_version = models.CharField('系统版本', max_length=16, null=True, blank=True)
            main_board = info['main_board']['data']
            cpu = info['cpu']['data']
            print("CPU",cpu)
            #将三个字典 更新（加入） server_info字典中
            server_info.update(basic)
            server_info.update(main_board)
            server_info.update(cpu)

            print("server_info",server_info)
            #打散字典，将数据插入到Server数据表
            server = models.Server.objects.create(**server_info)
        ######👇 ###新增Disk
            #disk 数据 结构：
            # 'disk': {
            #     'status': True,
            #     'error': '',
            #     'data': {
            #         '0': {
            #             'slot': '0',
            #             'pd_type': 'SAS',
            #             'capacity': '279.396',
            #             'model': 'SEAGATE ST300MM0006 LS08S0K2B5NV'
            #         },
            #         '1': {
            #             'slot': '1',
            #             'pd_type': 'SAS',
            #             'capacity': '279.396',
            #             'model': 'SEAGATE ST300MM0006 LS08S0K2B5AH'
            #         },
            #         '2': {
            #             'slot': '2',
            #             'pd_type': 'SATA',
            #             'capacity': '476.939',
            #             'model': 'S1SZNSAFA01085L Samsung SSD 850 PRO 512GB EXM01B6Q'
            #         },
            disk_info=info["disk"]["data"]
            print(disk_info)
            #{'0': {'slot': '0', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'},
            # '1': {'slot': '1', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH'}......


            #disk 表字段
            # slot = models.CharField('插槽位', max_length=8)
            # model = models.CharField('磁盘型号', max_length=108)
            # capacity = models.FloatField('磁盘容量GB')
            # pd_type = models.CharField('磁盘类型', max_length=32)
            #
            # server = models.ForeignKey(verbose_name='服务器', to='Server', related_name='disk_list',
            #                            on_delete=models.CASCADE)

            #生成一个列表,将对象存入列表中（按照上面的方法，如果此时有多块硬盘，就需要循环多次，每次都要连接数据库，现在这里要批量插入bulk_create）
            disk_obj_list = []
            for disk in disk_info.values():
                #取disk_info value值，打散，但还有个外键字段server
                # (server(外键字段)=server(上面的server对象   server = models.Server.objects.create(**server_info) )），将models.Disk(**disk, server=server)对象追加进列表
                disk_obj_list.append(models.Disk(**disk, server=server))
            #如果列表有内容
            if disk_obj_list:
                #批量插入(不管列表中有几个对象,一次性插入，只连接数据库一次)
                models.Disk.objects.bulk_create(disk_obj_list)
        ###👇##新增Memory
            memory_info = info['memory']['data']
            memory_obj_list = []
            for memory in memory_info.values():
                memory_obj_list.append(models.Memory(**memory, server=server))
            if memory_obj_list:
                models.Memory.objects.bulk_create(memory_obj_list)
        ###👇##新增Nic
            nic_info = info['nic']['data']
            nic_obj_list = []
            for name, nic in nic_info.items():
                nic_obj_list.append(models.NIC(**nic, name=name, server=server))
            if nic_obj_list:
                models.NIC.objects.bulk_create(nic_obj_list)


        elif action == 'update' or action == 'update_host':
        # 只更新资产信息 或者  更新 资产+主机名
            server = process_basic(info)
            process_disk(info, server)
            process_memory(info, server)
            process_nic(info, server)


        #返回数据（字典）
        return Response(result)