# coding: utf-8
from base import *

func_config = {
    # "tag_index" : ( is_open, "func_name")
    0: (False, 'Reserve'),
    1: (False, 'Reserve'),
    2: (False, 'Reserve'),
    3: (True, 'coin'),  # 实时报价
    4: (True, 'auto_reply'),  # 自动回复
    5: (True, 'batch_sending'),  # 发送信息（群发）
    6: (True, 'wallet'),  # 钱包
    7: (True, 'events'),  # 社群拉新
    8: (True, 'statis'),  # 数据分析
    9: (True, 'sensitive'),  # 敏感词监控（群消息监控）
    10: (True, 'group_zone'),  # 群空间
    11: (True, 'employee'),  # 业务员监控 # 尚层
    12: (True, 'assistant'),  # 小助手管理
    13: (True, 'share_task'),  # 链接追踪
}


class Tag:
    default_config = {
        'yaca': [3, 4, 5, 6, 7, 8, 9, 10, 12, 13],
        'zidou': [4, 5, 7, 8, 9, 10, 12, 13],
        'test': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    }
    default_display_config = {
        'yaca': [3, 4, 5, 6, 7, 8, 9, 10, 12, 13],
        'zidou': [4, 5, 7, 8, 9, 10, 12, 13],
        'test': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    }

    def __init__(self, bitmap=0):
        self.bitmap = bitmap

    def get_tag(self, tag):
        return _get_tag(self.bitmap, tag)

    def get_tags(self):
        return _get_tags(self.bitmap)

    def put_tag(self, tag_id):
        self.bitmap = _put_tag(self.bitmap, tag_id)
        return True

    def put_tags(self, tag_list):
        self.bitmap = _put_tags(self.bitmap, tag_list)
        return True

    def delete_tag(self, tag_id):
        self.bitmap = _delete_tag(self.bitmap, tag_id)
        return True

    def delete_tags(self, tag_list):
        self.bitmap = _delete_tags(self.bitmap, tag_list)
        return True

    def get_name(self, name):
        if name in self.get_open_name_list():
            return True
        return False

    def get_names(self):
        return self.get_open_name_list()

    def put_name(self, name):
        for k, v in func_config.items():
            if v[1] == name:
                self.put_tag(k)
                return self
        raise NameError('Error tag name:%s' % name)

    def put_names(self, name_list):
        tag_list = []
        for k, v in func_config.items():
            if v[1] in name_list:
                tag_list.append(k)
        self.put_tags(tag_list)
        return self

    def delete_name(self, name):
        for k, v in func_config.items():
            if v[1] == name:
                self.delete_tag(k)
                return self
        raise NameError('Error tag name:%s' % name)

    def delete_names(self, name_list):
        tag_list = []
        for k, v in func_config.items():
            if v[1] in name_list:
                tag_list.append(k)
        self.delete_tags(tag_list)
        return self

    def load_config(self, app_name):
        if app_name in self.default_config:
            tag_list = self.default_config[app_name]
        else:
            raise RuntimeError('Can not load this config:%s' % app_name)
        self.put_tags(tag_list)
        return self

    def as_int(self):
        return self.bitmap

    def get_open_name_list(self):
        return [func_config[i][1] for i in func_config.keys() if (i in self.get_tags() and func_config[i][0])]

    def get_name_dict(self):
        res = {}
        open_name_list = self.get_open_name_list()
        for k, v in func_config.items():
            if v[0]:
                if v[1] in open_name_list:
                    res[v[1]] = True
                else:
                    res[v[1]] = False
        return res

    def get_close_name_list(self):
        return [i[1] for i in func_config.values() if (i[1] not in self.get_open_name_list() and i[0])]

    def __repr__(self):
        return str(self.get_open_name_list())

    def __iter__(self):
        return (i for i in self.get_open_name_list())
print(Tag().load_config('test'))