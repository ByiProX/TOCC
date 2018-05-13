# -*- coding: utf-8 -*-
# import threading
#
# from flask import request
#
# from configs.config import main_api, SUCCESS, ERR_USER_TOKEN, ERR_CIRCLE_STATUS_WRONG
# from core.consumption_core import consumption_thread, ConsumptionThread
# from core.production_core import production_thread, ProductionThread
# from utils.u_response import make_response
#
#
# @main_api.route('/open_production_circle', methods=['POST'])
# def app_open_production_circle():
#     """
#     用于开启生产循环
#     {"bCzPSCtVkZtPRU53":"24oInHpWUhxXRqSA","VzIRzIRf3Lqzq3GT":"b2jeMQ0y99V2Gnlp"}
#     """
#     b = request.json.get('bCzPSCtVkZtPRU53')
#     v = request.json.get('VzIRzIRf3Lqzq3GT')
#
#     if b == "24oInHpWUhxXRqSA" and v == "b2jeMQ0y99V2Gnlp":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'pcwiyQgeoilnoBkS':
#                 start_flag = True
#                 break
#
#         if start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         production_thread.start()
#         return make_response(SUCCESS)
#     else:
#         return make_response(ERR_USER_TOKEN)
#
#
# @main_api.route('/open_consumption_circle', methods=['POST'])
# def app_open_consumption_circle():
#     """
#     用于开启消费循环
#     {"v0MncGVyVronZpt3":"zU2s5T67wPfvybPp","jNSLvKzUWlzoQIAY":"9Fjfrbd7i9j3fBnV"}
#     """
#     b = request.json.get('v0MncGVyVronZpt3')
#     v = request.json.get('jNSLvKzUWlzoQIAY')
#
#     if b == "zU2s5T67wPfvybPp" and v == "9Fjfrbd7i9j3fBnV":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'zBh8cb6VK11w6F1l':
#                 start_flag = True
#                 break
#
#         if start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         consumption_thread.start()
#         return make_response(SUCCESS)
#     else:
#         return make_response(ERR_USER_TOKEN)
#
#
# @main_api.route('/stop_production_circle', methods=['POST'])
# def app_stop_production_circle():
#     """
#     关闭生产循环
#     :return:
#     """
#     b = request.json.get('bCzPSCtVkZtPRU53')
#     v = request.json.get('VzIRzIRf3Lqzq3GT')
#
#     if b == "24oInHpWUhxXRqSA" and v == "b2jeMQ0y99V2Gnlp":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'pcwiyQgeoilnoBkS':
#                 start_flag = True
#                 t.stop()
#                 break
#
#         if not start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         return make_response(SUCCESS)
#     else:
#         return make_response(ERR_USER_TOKEN)
#
#
# @main_api.route('/stop_consumption_circle', methods=['POST'])
# def app_stop_consumption_circle():
#     """
#     关闭消费循环
#     :return:
#     """
#     b = request.json.get('v0MncGVyVronZpt3')
#     v = request.json.get('jNSLvKzUWlzoQIAY')
#
#     if b == "zU2s5T67wPfvybPp" and v == "9Fjfrbd7i9j3fBnV":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'zBh8cb6VK11w6F1l':
#                 start_flag = True
#                 t.stop()
#                 break
#
#         if not start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         return make_response(SUCCESS)
#     else:
#         return make_response(ERR_USER_TOKEN)
#
#
# @main_api.route('/restart_production_circle', methods=['POST'])
# def app_restart_production_circle():
#     """
#     重启生产循环
#     :return:
#     """
#     b = request.json.get('bCzPSCtVkZtPRU53')
#     v = request.json.get('VzIRzIRf3Lqzq3GT')
#
#     if b == "24oInHpWUhxXRqSA" and v == "b2jeMQ0y99V2Gnlp":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'pcwiyQgeoilnoBkS':
#                 start_flag = True
#                 t.stop()
#         if not start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         else:
#             production_thread_new = ProductionThread(thread_id='pcwiyQgeoilnoBkS')
#             production_thread_new.start()
#     else:
#         return make_response(ERR_USER_TOKEN)
#
#
# @main_api.route('/restart_consumption_circle', methods=['POST'])
# def app_restart_consumption_circle():
#     """
#     关闭消费循环
#     :return:
#     """
#     b = request.json.get('v0MncGVyVronZpt3')
#     v = request.json.get('jNSLvKzUWlzoQIAY')
#
#     if b == "zU2s5T67wPfvybPp" and v == "9Fjfrbd7i9j3fBnV":
#         threading_list = threading.enumerate()
#         start_flag = False
#         for t in threading_list:
#             if t.name == 'zBh8cb6VK11w6F1l':
#                 start_flag = True
#                 t.stop()
#         if not start_flag:
#             return make_response(ERR_CIRCLE_STATUS_WRONG)
#         else:
#             consumption_thread_new = ConsumptionThread(thread_id='zBh8cb6VK11w6F1l')
#             consumption_thread_new.start()
#     else:
#         return make_response(ERR_USER_TOKEN)
