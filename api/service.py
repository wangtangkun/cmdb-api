from repository import models



def process_basic(info):
    '''
    服务器基本信息  更新 删除 新增
    :param info:
    :return:
    '''
    server_info = {}



    basic = info['basic']['data']
    main_board = info['main_board']['data']
    cpu = info['cpu']['data']
    server_info.update(basic)
    server_info.update(main_board)
    server_info.update(cpu)

    hostname = info['basic']['data']['hostname']  # 新的hostname
    print("当前hostname", hostname)


    old_hostname = info.get('old_hostname')  # 老的hostname
    print("老hostname",old_hostname)


    #根据主机名字段查询数据库对象，如果有老主机名就要老主机名查询。
    server_list = models.Server.objects.filter(hostname=old_hostname if old_hostname else hostname)

    #数据将数据库中刚查询到的对象更新
        #只更新资产（不存在old_hostname）,更新后主机名没变。
        #更新资产 + 主机名   （以old_hostname查询出对象,更新后资产和主机名 都被更新）
    server_list.update(**server_info)

    #根据主机名查询对象（更新后的对象）
    server = models.Server.objects.filter(hostname=hostname).first()

    #返回对象
    return server


def process_disk(info, server):
    '''
    硬盘信息  更新 删除 新增
    :param info:
    :param server:
    :return:
    '''


    disk_info = info['disk']['data']  # 新提交的数据
   # print(disk_info) #{'0': {'slot': '0', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'},
                    # '1': {'slot': '1', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH'}... }


    #将disk_info变为集合,自动只取key值,实际取槽位, 集合类型
    disk_slot_set = set(disk_info)
    #print("disk_slot_set",disk_slot_set)  #disk_slot_set {'5', '2', '1', '0', '3', '4'}

    #根据server对象取对应的硬盘信息, 只取slot字段（槽位）,集合类型
    disk_slot__db_set = {i.slot for i in models.Disk.objects.filter(server=server)}
    #print("disk_slot__db_set",disk_slot__db_set) #disk_slot__db_set {'5', '1', '0', '3', '2', '4'}



    #新增数据中 与数据库数据中 槽位对比确定  新增  删除  更新等操作
    #差集
    add_slot_set = disk_slot_set - disk_slot__db_set  # 新增的槽位
    print("新增的槽位",add_slot_set)
    # 差集
    del_slot_set = disk_slot__db_set - disk_slot_set  # 删除的槽位
    print("删除的槽位", del_slot_set)

    #并集  两个集合中都存在的
    update_slot_set = disk_slot__db_set & disk_slot_set  # 更新的槽位
    print("更新的槽位", update_slot_set)

    # 新增硬盘

    #将新增的硬盘对象加入列表
    add_disk_lit = []

    #资产修改信息列表（列表内追加数据对象）,用于后面批量插入
    add_record_list = []

    #循环新增集合
    for slot in add_slot_set:
        disk = disk_info.get(slot)
        """
               disk 数据结构:
                {
                   'slot': '0',
                   'pd_type': 'SAS',
                   'capacity': '279.396',
                   'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'
               }

               """
        #存放新增硬盘信息列表
        tpl_list = []  # ['插槽位 : 0', '磁盘类型 : SAS', '磁盘容量GB : 279.396', '磁盘型号 : SEAGATE ST300MM0006     LS08S0K2B5NV']
        for name, value in disk.items():
            verbose_name = models.Disk._meta.get_field(name).verbose_name
            #数据追加到tpl_list列表中
            tpl_list.append("{}:{}".format(verbose_name, value))  # 插槽位 : 0    磁盘型号: SAS

        #AssetRecord数据对象追加到列表中
        add_record_list.append(
            #根据AssetRecord数据表的字段,创造对象
            models.AssetRecord(server=server, content="新增硬盘，硬盘详细信息如下：{}".format('; '.join(tpl_list))))

        #Disk 数据对象追加到列表中
        add_disk_lit.append(models.Disk(**disk, server=server))

    #列表存在内容，批量（AssetRecord数据对象（资产修改表）、Disk（硬盘表） 数据对象）创建到数据库
    if add_disk_lit:
        models.Disk.objects.bulk_create(add_disk_lit)
        models.AssetRecord.objects.bulk_create(add_record_list)

    # 如果del_slot_set集合存在内容（删除硬盘）
    if del_slot_set:
        # 数据库 server对象相同，并solt字段内容 存在于del_slot_set 集合中的对象，删除
        models.Disk.objects.filter(server=server, slot__in=del_slot_set).delete()
        models.AssetRecord.objects.create(server=server, content='槽位{}的硬盘被移除了'.format(','.join(del_slot_set)))
    # 更新硬盘
    update_record_list = []  # 变更记录对象的列表
    for slot in update_slot_set:
        disk = disk_info.get(slot)  # 新提交的数据
        disk_obj = models.Disk.objects.filter(server=server, slot=slot).first()  # 老硬盘的对象

        tpl_list = []  # 临时存放

        update_dict = {}  # 更新字段的值
        for name, value in disk.items():
            old_value = getattr(disk_obj, name)  #老硬盘对象+name  通过反射获取老的值

            #如果新值与老的值不相等（更新）
            if value != str(old_value):
                #将数据加入字典  字段名（例如solt、pd_type）:新值
                update_dict[name] = value
                verbose_name = models.Disk._meta.get_field(name).verbose_name
                #verbose_name   老的值  新的值
                tpl_list.append("{}由{}变更为{}".format(verbose_name, old_value, value))
        #如果tpl_list True（存在更新）
        if tpl_list:
            update_record_list.append(
                models.AssetRecord(server=server, content='槽位{}上的硬盘发生变更，变更信息如下：{}'.format(slot, '; '.join(tpl_list))))
            #更新Disk数据对象  根据solt一条条更新（更新需要一对一，不能批量）
            models.Disk.objects.filter(server=server, slot=slot).update(**update_dict)
    #如果update_record_list True（存在更新）
    if update_record_list:
        #批量创建AssetRecord数据对象
        models.AssetRecord.objects.bulk_create(update_record_list)


def process_memory(info, server):
    '''
    内存信息 更新  删除 新增
    :param info:
    :param server:
    :return:
    '''
    # 更新内存
    memory_info = info['memory']['data']  # 新提交的数据

    memory_slot_set = set(memory_info)
    memory_slot__db_set = {i.slot for i in models.Memory.objects.filter(server=server)}

    # 新增  删除  更新
    add_slot_set = memory_slot_set - memory_slot__db_set  # 新增的槽位
    del_slot_set = memory_slot__db_set - memory_slot_set  # 删除的槽位
    update_slot_set = memory_slot__db_set & memory_slot_set  # 更新的槽位

    # 新增内存

    add_memory_lit = []
    for slot in add_slot_set:
        memory = memory_info.get(slot)
        add_memory_lit.append(models.Memory(**memory, server=server))

    if add_memory_lit:
        models.Memory.objects.bulk_create(add_memory_lit)

    # 删除内存
    if del_slot_set:
        models.Memory.objects.filter(server=server, slot__in=del_slot_set).delete()

    # 更新内存
    for slot in update_slot_set:
        memory = memory_info.get(slot)
        print("memory",memory)
        models.Memory.objects.filter(server=server, slot=slot).update(**memory)


def process_nic(info, server):
    '''
    网卡信息  更新 删除 新增
    :param info:
    :param server:
    :return:
    '''
    nic_info = info['nic']['data']  # 新提交的数据

    nic_name_set = set(nic_info)
    nic_name__db_set = {i.name for i in models.NIC.objects.filter(server=server)}

    # 新增  删除  更新
    add_name_set = nic_name_set - nic_name__db_set  # 新增的槽位
    del_name_set = nic_name__db_set - nic_name_set  # 删除的槽位
    update_name_set = nic_name__db_set & nic_name_set  # 更新的槽位

    # 新增网卡

    add_nic_lit = []
    for name in add_name_set:
        nic = nic_info.get(name)
        nic['name'] = name
        add_nic_lit.append(models.NIC(**nic, server=server))

    if add_nic_lit:
        models.NIC.objects.bulk_create(add_nic_lit)

    # 删除网卡
    if del_name_set:
        models.NIC.objects.filter(server=server, name__in=del_name_set).delete()

    # 更新网卡
    for name in update_name_set:
        nic = nic_info.get(name)
        nic['name'] = name
        models.NIC.objects.filter(server=server, name=name).update(**nic)
