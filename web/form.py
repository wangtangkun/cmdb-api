#！/usr/bin/env python
#-*- coding:utf-8 -*-

from django import forms
from repository import models

class ServerForm(forms.ModelForm):
    class Meta:
        model = models.Server
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("self.fields.values()",self.fields.values())
        print("device_status_id", self.fields["device_status_id"])
        for filed in self.fields.values():
                #给每个字段在前端展示 新增样式
            if filed == self.fields["device_status_id"] or filed ==self.fields["cabinet_num"]or filed ==self.fields["idc"]or filed ==self.fields["cabinet_order"]or filed ==self.fields["business_unit"]  :
                filed.widget.attrs['class'] = 'form-control' #样式

            else:
                #除了上面的字段，其他字段不能在页面编辑
                filed.widget.attrs['disabled'] = 'disabled'  # 不能编辑
                filed.widget.attrs['class'] = 'form-control'  # 样式