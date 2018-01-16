#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com
def get_info(line):
    line_list = line.strip().split()
    id = line_list[0]
    location = [int(i) for i in line_list[1:4]]
    if len(line_list) > 4:
        offset = [int(i) for i in line_list[4:7]]
        new_location = [location[i] + offset[i] for i in range(len(location))]
        info = dict(zip(('ID', 'location', 'offset', 'new_location'),
                         (id, location, offset, new_location)))
    else:
        info = dict(zip(('ID', 'location'), (id, location)))
    return info


def get_valid_signal(file):
    valid_signal_list = []
    with open(file, 'r') as fo:
        line = fo.readline()
        valid_signal_list.append(get_info(line))
        while True:
            line = fo.readline()
            if len(line.strip().split()) > 4:
                valid_signal_list.append(get_info(line))
            else:
                break
    return valid_signal_list


def get_all_signal_line_num(file):
    with open(file, 'r') as fo:
        line_num = len(fo.readlines())
    return line_num
