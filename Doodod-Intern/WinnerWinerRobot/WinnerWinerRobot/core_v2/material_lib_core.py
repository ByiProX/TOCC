# -*- coding: utf-8 -*-
__author__ = "Quentin"

from configs.config import ERR_WRONG_ITEM
from models_v2.base_model import BaseModel

import logging

logger = logging.getLogger('main')
SENSITIVE_WORD_RULE_DICT = {}


def delete_a_material(client_id, msg_id):
    material = BaseModel.fetch_one("material_lib", "*",
                                   where_clause=BaseModel.where_dict({"client_id": client_id, "msg_id": msg_id}))

    if not material:
        return ERR_WRONG_ITEM

    material.delete()
