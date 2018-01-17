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
    def test_is_true_format(self):
        line0 = 'plane1 1 1\n'
        line1 = 'plane1 1 1 1 2 3\n'
        line2 = 'plane1 ? 2 3 4 5 1\n'
        line3 = 'plane1 w e 1 3 43 2\n'
        line4 = 'plane1 2 4 1 3 43 2\n'
        line5 = '? 2 4 1 3 43 2\n'

        self.assertEqual(method_func.is_true_format(line0), False)
        self.assertEqual(method_func.is_true_format(line1), False)
        self.assertEqual(method_func.is_true_format(line2), False)
        self.assertEqual(method_func.is_true_format(line3), False)
        self.assertEqual(method_func.is_true_format(line4), True)
        self.assertEqual(method_func.is_true_format(line5), False)


    def test_is_integer(self):
        list0 = ['0', '-1', '+1']
        list1 = ['1', '1.1', '-1']
        list2 = ['a', '0', '-1']
        list3 = ['0', '1', '2', '-1', '+2', '+0']

        self.assertEqual(method_func.is_integer(list0), True)
        self.assertEqual(method_func.is_integer(list1), False)
        self.assertEqual(method_func.is_integer(list2), False)
        self.assertEqual(method_func.is_integer(list3), True)


    def test_get_valid_signal(self):
        file = 'testcase/test_signal.txt'
        '''test_signal.txt
        plane1 1 1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 3 4 5
        plane1 1 1 1 1 2 3
        '''
        self.assertTrue(isinstance(method_func.get_valid_signal(file), list))
        self.assertEqual(method_func.get_valid_signal(file),
                        [{'ID': 'plane1', 'location': [1, 1, 1], 'new_location': [1, 1, 1]},
                         {'ID': 'plane1', 'location': [1, 1, 1], 'new_location': [2, 3, 4], 'offset': [1, 2, 3]},
                         {'ID': 'plane1', 'location': [2, 3, 4], 'new_location': [3, 4, 5], 'offset': [1, 1, 1]}])

    def test_get_all_signal_line_num(self):
        file = 'testcase/test_signal.txt'
        '''test_signal.txt
        plane1 1 1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 3 4 5
        plane1 1 1 1 1 2 3
        '''

        self.assertTrue(isinstance(method_func.get_all_signal_line_num(file), int))
        self.assertEqual(method_func.get_all_signal_line_num(file), 5)

    def test_check(self):
        file0 = 'testcase/test_signal_no_data.txt'
        file1 = 'testcase/test_signal.txt'
        '''test_signal.txt
        plane1 1 1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 3 4 5
        plane1 1 1 1 1 2 3
        '''

        # 边缘测试
        self.assertEqual(check(file0, 2), 'No Datas in target file!')
        self.assertEqual(check(file1, 0), 'plane1 0 1 1 1')
        self.assertEqual(check(file1, 3), 'Error: 3')
        self.assertEqual(check(file1, 5), 'Cannot find 5')
        # 常规测试
        self.assertEqual(check(file1, 2), 'plane1 2 3 4 5')
        self.assertEqual(check(file1, 4), 'Error: 4')
        self.assertEqual(check(file1, 100), 'Cannot find 100')

    def test_format(self):
        file0 = 'testcase/test_error_format0.txt'
        file1 = 'testcase/test_error_format1.txt'
        '''test_error_format0.txt
        plane1  1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 3 4 5 0 -1 -2
        plane1 3 3 3 0 0 6
        '''
        '''test_error_format1.txt
        plane1 1 1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 ? 5 0 -1 -2
        plane1 3 3 3 0 0 6
        '''

        self.assertEqual(check(file0, 0), 'Error: 0')
        self.assertEqual(check(file0, 1), 'Error: 1')
        self.assertEqual(check(file0, 2), 'Error: 2')
        self.assertEqual(check(file0, 3), 'Error: 3')
        self.assertEqual(check(file0, 4), 'Error: 4')
        self.assertEqual(check(file0, 5), 'Cannot find 5')
        self.assertEqual(check(file0, 100), 'Cannot find 100')

        self.assertEqual(check(file1, 0), 'plane1 0 1 1 1')
        self.assertEqual(check(file1, 1), 'plane1 1 2 3 4')
        self.assertEqual(check(file1, 2), 'plane1 2 3 4 5')
        self.assertEqual(check(file1, 3), 'Error: 3')
        self.assertEqual(check(file1, 4), 'Error: 4')
        self.assertEqual(check(file1, 5), 'Cannot find 5')
        self.assertEqual(check(file1, 100), 'Cannot find 100')

    def test_location(self):
        file0 = 'testcase/test_error_location0.txt'
        file1 = 'testcase/test_error_location1.txt'
        '''test_error_location0.txt
        plane1 1 1 1
        plane1 0 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 3 4 5 1 1 1
        plane1 1 1 1 1 2 3
        '''
        '''test_error_location1.txt
        plane1 1 1 1
        plane1 1 1 1 1 2 3
        plane1 2 3 4 1 1 1
        plane1 0 4 5 1 1 1
        plane1 1 5 6 1 2 3
        '''

        self.assertEqual(check(file0, 0), 'plane1 0 1 1 1')
        self.assertEqual(check(file0, 1), 'Error: 1')
        self.assertEqual(check(file0, 2), 'Error: 2')
        self.assertEqual(check(file0, 3), 'Error: 3')
        self.assertEqual(check(file0, 4), 'Error: 4')
        self.assertEqual(check(file0, 5), 'Cannot find 5')
        self.assertEqual(check(file0, 100), 'Cannot find 100')

        self.assertEqual(check(file1, 0), 'plane1 0 1 1 1')
        self.assertEqual(check(file1, 1), 'plane1 1 2 3 4')
        self.assertEqual(check(file1, 2), 'plane1 2 3 4 5')
        self.assertEqual(check(file1, 3), 'Error: 3')
        self.assertEqual(check(file1, 4), 'Error: 4')
        self.assertEqual(check(file1, 5), 'Cannot find 5')
        self.assertEqual(check(file1, 100), 'Cannot find 100')

    def test_number_with_sign(self):
        file0 = 'testcase/test_number_with_sign.txt'
        '''test_number_with_sign.txt
        plane1 2 2 2
        plane1 2 2 2 1 1 1
        plane1 3 3 3 1 2 3
        plane1 4 5 6 0 0 0
        plane1 4 5 6 -1 -1 -1
        plane1 3 4 5 +1 +1 +1
        plane1 4 5 6 3 -3 -3
        plane1 1 2 3 0 -1 -1
        plane1 1 1 1
        plane1 1 1 1 2 3 4
        '''

        self.assertEqual(check(file0, 0), 'plane1 0 2 2 2')
        self.assertEqual(check(file0, 1), 'plane1 1 3 3 3')
        self.assertEqual(check(file0, 2), 'plane1 2 4 5 6')
        self.assertEqual(check(file0, 3), 'plane1 3 4 5 6')
        self.assertEqual(check(file0, 4), 'plane1 4 3 4 5')
        self.assertEqual(check(file0, 5), 'plane1 5 4 5 6')
        self.assertEqual(check(file0, 6), 'plane1 6 7 2 3')
        self.assertEqual(check(file0, 7), 'Error: 7')
        self.assertEqual(check(file0, 9), 'Error: 9')
        self.assertEqual(check(file0, 10), 'Cannot find 10')


if __name__ == '__main__':
        unittest.main()
