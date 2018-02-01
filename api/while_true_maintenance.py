# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import main_api, SUCCESS, ERR_USER_TOKEN
from core.consumption_core import consumption_thread
from core.production_core import production_thread
from utils.u_response import make_response


@main_api.route('/open_production_circle', methods=['POST'])
def app_open_production_circle():
    """
    用于开启生产循环
    {"bCzPSCtVkZtPRU53":"24oInHpWUhxXRqSA","VzIRzIRf3Lqzq3GT":"b2jeMQ0y99V2Gnlp"}
    """
    bCzPSCtVkZtPRU53 = request.json.get('bCzPSCtVkZtPRU53')
    VzIRzIRf3Lqzq3GT = request.json.get('VzIRzIRf3Lqzq3GT')

    if bCzPSCtVkZtPRU53 == "24oInHpWUhxXRqSA" and VzIRzIRf3Lqzq3GT == "b2jeMQ0y99V2Gnlp":
        production_thread.start()
        return make_response(SUCCESS)
    else:
        return make_response(ERR_USER_TOKEN)


@main_api.route('/open_consumption_circle', methods=['POST'])
def app_open_consumption_circle():
    """
    用于开启生产循环
    {"v0MncGVyVronZpt3":"zU2s5T67wPfvybPp","jNSLvKzUWlzoQIAY":"9Fjfrbd7i9j3fBnV"}
    """
    v0MncGVyVronZpt3 = request.json.get('v0MncGVyVronZpt3')
    jNSLvKzUWlzoQIAY = request.json.get('jNSLvKzUWlzoQIAY')

    if v0MncGVyVronZpt3 == "zU2s5T67wPfvybPp" and jNSLvKzUWlzoQIAY == "9Fjfrbd7i9j3fBnV":
        consumption_thread.start()
        return make_response(SUCCESS)
    else:
        return make_response(ERR_USER_TOKEN)
