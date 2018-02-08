#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com
import sys
import mymethod


def reminder(test='test1'):
    """main codes"""
    # 使用上下文管理器打开文件
    with open(test + '.txt', 'r') as fo:
        # 读取第一行获取提交的信息
        line = fo.readline()
        submit_date = mymethod.get_date(line)

        # 创建三个字典用于存储保养提醒车辆的相关信息
        time_related_maintain = {}
        distance_related_maintain = {}
        write_off = {}

        # 循环读取后续各行并分类存储到三个字典
        while True:
            line = fo.readline()
            if line:
                car_info = mymethod.get_car_info(line)

                # 如果已经报废，中断当前循环，继续下一层循环，即放弃当前行继续下一行
                if mymethod.is_write_off(line, submit_date) == 'wrote off':
                    continue

                # 判断是否将要报废，如果将要报废的话继续执行内层代码
                elif mymethod.is_write_off(line, submit_date):
                    # 如果字典中没有该车辆的相关信息，给字典添加该车辆信息
                    if car_info['brand'] not in write_off.keys():
                        write_off[car_info['brand']] = {'num': 1, 'plate_num': [car_info['plate_num']]}

                    # 如果字典中存在该车辆的信息，那么更新字典的值
                    else:
                        write_off[car_info['brand']]['num'] += 1
                        write_off[car_info['brand']]['plate_num'].append(car_info['plate_num'])

                # 判断是否满足每一万公里保养提醒，若值为True，执行内部代码
                elif mymethod.is_distance_related_maintain(line):
                    # 如果字典中没有该车辆的相关信息，给字典添加该车辆信息
                    if car_info['brand'] not in distance_related_maintain.keys():
                        distance_related_maintain[car_info['brand']] = {'num': 1, 'plate_num': [car_info['plate_num']]}

                    # 如果字典中存在该车辆的信息，那么更新字典的值
                    else:
                        distance_related_maintain[car_info['brand']]['num'] += 1
                        distance_related_maintain[car_info['brand']]['plate_num'].append(car_info['plate_num'])

                # 判断是否满足定期保养提醒，若值为True，执行内部代码
                elif mymethod.is_time_related_maintain(line, submit_date):
                    # 如果字典中没有该车辆的相关信息，给字典添加该车辆信息
                    if car_info['brand'] not in time_related_maintain.keys():
                        time_related_maintain[car_info['brand']] = {'num': 1, 'plate_num': [car_info['plate_num']]}

                    # 如果字典中存在该车辆的信息，那么更新字典的值
                    else:
                        time_related_maintain[car_info['brand']]['num'] += 1
                        time_related_maintain[car_info['brand']]['plate_num'].append(car_info['plate_num'])

            # 读取文档结尾处，循环结束，跳出循环
            else:
                break

    # 按要求打印输出结果
    mymethod.print_result(time_related_maintain, distance_related_maintain, write_off)


if __name__ == '__main__':
    try:
        reminder(sys.argv[1])
    except IndexError:
        reminder()
    except FileNotFoundError:
        print('No such a file, please input right filename.')
