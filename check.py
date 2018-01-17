#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com
import sys
import method_func


def check(file, signal_index):
    '''逻辑分析，输出判断'''
    all_line_num = method_func.get_all_signal_line_num(file)
    if all_line_num == 0:  # 空文件
        return 'No Datas in target file!'

    valid_signal_list = method_func.get_valid_signal(file)
    valid_line_num = len(valid_signal_list)

    if signal_index >= all_line_num:  # 指定消息不存在
        return 'Cannot find ' + str(signal_index)
    elif all_line_num > signal_index >= valid_line_num:  # 指定消息存在，无人机故障
        return 'Error: ' + str(signal_index)
    else:  # 指定消息存在，无人机正常
        result = valid_signal_list[signal_index]['ID'] + ' ' + str(signal_index) + ' ' + \
                ' '.join([str(i) for i in valid_signal_list[signal_index]['new_location']])
        return result


if __name__ == '__main__':
    try:
        print(check(sys.argv[1], int(sys.argv[2])))
    except FileNotFoundError:
        print('No such a file, please input right file path.')
    except (IndexError, ValueError):
        print('''
                ==========================================
                     The right way to run the code is：
                  python3 check.py filename signal_index
                ------------------------------------------
                For example: python3 check.py signal.txt 2
                ==========================================
              ''')
