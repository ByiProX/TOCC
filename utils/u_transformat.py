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
        return round_decimal(decimal.Decimal(_str))
    else:
        return round_decimal(decimal.Decimal(u'0'))


def round_decimal(dec):
    return dec.quantize(decimal.Decimal('1.00'), rounding = decimal.ROUND_05UP)


def decimal_to_str(a_decimal):
    if isinstance(a_decimal, decimal.Decimal):
        pass
    a_str = a_decimal.to_eng_string()
    if "." in a_str:
        a_split = a_str.split(".")
        while True:
            if len(a_split[1]) == 0:
                return a_split[0] + ".00"
            if a_split[1][-1] == "0":
                a_split[1] = a_split[1][:-1]
            else:
                return a_split[0] + "." + a_split[1]
    else:
        return a_str
