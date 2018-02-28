# -*- coding: utf-8 -*-
import decimal
import logging

logger = logging.getLogger('main')


def str_to_unicode(txt):
    if isinstance(txt, str):
        txt = txt.decode(u'utf-8')
    elif isinstance(txt, unicode):
        pass
    else:
        raise TypeError(u'param is not (str and unicode)')
    return txt


def unicode_to_str(txt):
    if isinstance(txt, unicode):
        txt = txt.encode(u'utf-8')
    elif isinstance(txt, str):
        pass
    else:
        raise TypeError(u'param is not (str and unicode)')
    return txt


def str_to_decimal(_str):
    if _str and _str != u'None':
        return decimal.Decimal(_str)
    else:
        return decimal.Decimal(u'0')