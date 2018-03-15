# -*- coding: utf-8 -*-
from configs.config import db
from models.message_ext_models import MessageAnalysis

i = 300
while i < 67240:
    MessageAnalysis.count_msg_by_ids(i, i + 100)
    i += 300

pass
