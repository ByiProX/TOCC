#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com
import unittest
import method_func
from check import check

class Test(unittest.TestCase):
    """对每一个方法函数进行单元测试"""
    def test_get_info(self):
        line0 = 'plane1 1 1 1\n'
        self.assertTrue(isinstance(method_func.get_info(line0), dict))  # 类型判断
        self.assertEqual(method_func.get_info(line0), {
                                        'ID':'plane1',
                                        'location':[1, 1, 1],
                                        'new_location':[1, 1, 1]
                                        })  # 返回值判断
        line1 = 'plane1 1 1 1 1 2 3\n'
        self.assertTrue(isinstance(method_func.get_info(line1), dict))
        self.assertEqual(method_func.get_info(line1), {
                                        'ID':'plane1',
                                        'location':[1, 1, 1],
                                        'offset':[1, 2, 3],
                                        'new_location':[2, 3, 4]
                                        })

    def test_get_valid_signal(self):
        file = 'test_signal.txt'
        self.assertTrue(isinstance(method_func.get_valid_signal(file), list))
        self.assertEqual(method_func.get_valid_signal(file),
                        [{'ID': 'plane1', 'location': [1, 1, 1], 'new_location':[1, 1, 1]},
                         {'ID': 'plane1', 'location': [1, 1, 1], 'new_location': [2, 3, 4], 'offset': [1, 2, 3]},
                         {'ID': 'plane1', 'location': [2, 3, 4], 'new_location': [3, 4, 5], 'offset': [1, 1, 1]}])

    def test_get_all_signal_line_num(self):
        file = 'test_signal.txt'
        self.assertTrue(isinstance(method_func.get_all_signal_line_num(file), int))
        self.assertEqual(method_func.get_all_signal_line_num(file), 5)

    def test_check(self):
        file0 = 'test_signal_no_data.txt'
        file1 = 'test_signal.txt'

        # 边缘测试
        self.assertEqual(check(file0, 2), 'No Datas in target file!')
        self.assertEqual(check(file1, 0), 'plane1 0 1 1 1')
        self.assertEqual(check(file1, 3), 'Error: 3')
        self.assertEqual(check(file1, 5), 'Cannot find 5')
        # 常规测试
        self.assertEqual(check(file1, 2), 'plane1 2 3 4 5')
        self.assertEqual(check(file1, 4), 'Error: 4')
        self.assertEqual(check(file1, 100), 'Cannot find 100')


if __name__ == '__main__':
        unittest.main()
