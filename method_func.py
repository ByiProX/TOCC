#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com
from functools import reduce

def get_info(line):
    '''将每一行信息以字典的形式存储'''
    line_list = line.strip().split()
    id = line_list[0]
    location = [int(i) for i in line_list[1:4]]
    if len(line_list) > 4:
        offset = [int(i) for i in line_list[4:7]]
        new_location = [location[i] + offset[i] for i in range(len(location))]
        info = dict(zip(('ID', 'location', 'offset', 'new_location'),
                         (id, location, offset, new_location)))
    else:
        info = dict(zip(('ID', 'location', 'new_location'), (id, location, location)))
    return info


def is_true_format(line):
    '''数据类型判断'''
    line_list = line.strip().split()
    if len(line_list) == 4:
        if line_list[0].isalnum() and is_integer(line_list[1:]):
            return True
    if len(line_list) == 7:
        if line_list[0].isalnum() and is_integer(line_list[1:]):
            return True
    return False

def is_integer(line_list):
    '''列表元素是否为整形数字判断'''
    return reduce(lambda x, y: x and y, [i.strip('+-').isnumeric() for i in line_list])


def get_valid_signal(file):
    '''获取正常状态下的行，并将每行的数据以字典作为列表元素添加到列表中'''
    valid_signal_list = []
    with open(file, 'r') as fo:
        line = fo.readline() # 读取首行
        if line and len(line.strip().split()) == 4 and is_true_format(line): # 判断首行格式是否正确
            line_dict = get_info(line)
            valid_signal_list.append(line_dict)
        else:
            return valid_signal_list

        while True: # 从第二行开始遍历
            line = fo.readline()
            if line and len(line.strip().split()) == 7 and is_true_format(line): # 判断每行格式是否正确
                line_dict = get_info(line)
                # print(line_dict)
                former_location = valid_signal_list[-1]['new_location']
                location = line_dict['location']
                if former_location == location: # 判断前后两行位置是否一致
                    valid_signal_list.append(line_dict)
                else:
                    break
            else:
                break
    return valid_signal_list


def get_all_signal_line_num(file):
    '''获取数据文件的所有行数'''
    with open(file, 'r') as fo:
        line_num = len(fo.readlines())
    return line_num
