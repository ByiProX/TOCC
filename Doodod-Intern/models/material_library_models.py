# -*- coding: utf-8 -*-

from configs.config import db


class MaterialLibraryUser(db.Model):
    """
    记录用户的素材库
    """
    __tablename__ = "material_library_user"
    material_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    task_send_type = db.Column(db.Integer, index=True, nullable=False)
    task_send_content = db.Column(db.String(2048), index=True, nullable=False)

    used_count = db.Column(db.Integer, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    last_used_time = db.Column(db.DateTime, index=True, nullable=False)


class MaterialLibraryDefault(db.Model):
    """
    记录我们自己准备的素材模板
    其中该库为所有用户、所有群共有
    在没有改变的情况下，该库可以被读，但不能被写
    """
    __tablename__ = "material_library_default"
    dm_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    task_send_type = db.Column(db.Integer, index=True, nullable=False)
    task_send_content = db.Column(db.String(2048), index=True, nullable=False)

    used_count = db.Column(db.Integer, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    last_used_time = db.Column(db.DateTime, index=True, nullable=False)
