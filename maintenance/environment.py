# -*- coding: utf-8 -*-

import time
import logging
import requests
import psutil

from utils.u_email import EmailAlert

logger = logging.getLogger('main')


class ClientInfo:
    def __init__(self):
        self.ip_address = None
        self.client_name = ""
        self.continue_flag = True

        self.cpu_percent = 0.0
        self.memory_total = 0.0
        self.memory_free = 0.0
        self.memory_percent = 0.0
        self.swap_memory_total = 0.0
        self.swap_memory_available = 0.0
        self.swap_memory_percent = 0.0
        self.disk_dicts = dict()

    def automatic_detection(self):
        cpu_percent_list = []

        while self.continue_flag:

            self.get_my_ip_address()
            self.refresh_client_system_info()

            # 处理cpu
            if len(cpu_percent_list) >= 3:
                cpu_percent_list.pop(0)
            cpu_percent_list.append(self.cpu_percent)
            if self._get_list_average(cpu_percent_list) > 95.0:
                logger.warning(u"近期cpu使用率均值超过95%.")
                EmailAlert.send_it_alert(u"近期cpu使用率均值超过95%.")

            # 处理两个memory
            if self.swap_memory_percent > 95.0:
                logger.warning(u"当前交换内存占用率均值超过95%.")
                EmailAlert.send_it_alert(u"当前交换内存占用率均值超过95%.")

            if self.memory_percent > 95.0:
                logger.warning(u"当前物理内存占用率均值超过95%.")
                EmailAlert.send_it_alert(u"当前物理内存占用率均值超过95%.")

            # 处理硬盘
            for disk_name, disk_info in self.disk_dicts.items():
                if disk_info['percent'] > 95.0:
                    logger.warning(u"磁盘 %s 的占用空间已达到95%%." % disk_name)
                    EmailAlert.send_it_alert(u"磁盘 %s 的占用空间已达到95%%." % disk_name)

            time.sleep(120)

    def stop(self):
        self.continue_flag = False

    def get_my_ip_address(self):
        res = requests.get('http://members.3322.org/dyndns/getip')
        self.ip_address = res.text

    def refresh_client_system_info(self):
        # CPU
        self.cpu_percent = psutil.cpu_percent()

        # 真实内存
        self.memory_total = psutil.virtual_memory().total
        self.memory_free = psutil.virtual_memory().free
        self.memory_percent = float(1.0 - (float(self.memory_free) / float(self.memory_total))) * 100.0

        # 交换内存
        self.swap_memory_total = psutil.swap_memory().total
        self.swap_memory_available = psutil.swap_memory().free
        self.swap_memory_percent = psutil.swap_memory().percent

        # # 内存
        # self.virtual_memory_total = psutil.virtual_memory().total
        # self.virtual_memory_available = psutil.virtual_memory().available
        # self.virtual_memory_percent = psutil.virtual_memory().percent

        # 硬盘
        disk_partitions = psutil.disk_partitions()
        self.disk_dicts = {}
        for each_disk in disk_partitions:
            device_name = str(each_disk.mountpoint)
            self.disk_dicts.setdefault(device_name, {})
            self.disk_dicts[device_name] = {'total': psutil.disk_usage(device_name).total,
                                            'free': psutil.disk_usage(device_name).free,
                                            'percent': psutil.disk_usage(device_name).percent}

    @staticmethod
    def _get_list_average(a_list):
        return float(float(sum(a_list)) / float(len(a_list)))
