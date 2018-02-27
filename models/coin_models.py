# -*- coding: utf-8 -*-

from configs.config import db


class CoinInfo(db.Model):
    __tablename__ = 'coin_info'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    coin_name = db.Column(db.String(16), unique = True, index = True, nullable = False)
    open = db.Column()

