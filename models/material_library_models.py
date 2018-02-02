# -*- coding: utf-8 -*-

from configs.config import db


class UserMaterialLibrary(db.Model):
    """
    记录用户的素材库
    """
    __tablename__ = "user_material_library"
    material_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    task_send_type = db.Column(db.Integer, index=True, nullable=False)
    task_send_content = db.Column(db.String(2048), index=True, nullable=False)

    used_count = db.Column(db.Integer, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    last_used_time = db.Column(db.DateTime, index=True, nullable=False)
