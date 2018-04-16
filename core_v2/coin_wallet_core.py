# -*- coding: utf-8 -*-

import logging
import re
# import xlwt

from datetime import datetime

from sqlalchemy import func

from configs.config import db, SUCCESS, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM, UserQunR, Chatroom, Wallet
from models_v2.base_model import BaseModel, CM
from utils.u_time import datetime_to_timestamp_utc_8
from utils.u_transformat import str_to_unicode, unicode_to_str

logger = logging.getLogger('main')


# def get_members(user_info, uqun_id = None, limit = 10, offset = 0, member_username_except = None, keyword = None):
#     filter_list_members = list()
#     if keyword:
#         filter_list_members.append(AContact.nickname.like('%' + unicode_to_str(keyword) + '%'))
#     if member_username_except:
#         filter_list_members.append(AMember.username.notin_(member_username_except))
#     if uqun_id is not None:
#         filter_list_members.append(UserQunRelateInfo.uqun_id == uqun_id)
#     else:
#         filter_list_members.append(UserQunRelateInfo.user_id == user_info.user_id)
#
#     members_query = db.session.query(AMember.username, AContact) \
#         .outerjoin(UserQunRelateInfo, AMember.chatroomname == UserQunRelateInfo.chatroomname) \
#         .outerjoin(AContact, AMember.username == AContact.username) \
#         .group_by(AMember.username)\
#         .filter(*filter_list_members)
#     total_count = members_query.count()
#     rows = members_query.limit(limit).offset(offset).all()
#
#     member_json_list = list()
#     for row in rows:
#         # member_username = row[0]
#         a_contact = row[1]
#         member_json = dict()
#         # member_json['chatroom_id'] = uqun_id
#         member_json['member_id'] = a_contact.id
#         member_json['member_nickname'] = str_to_unicode(a_contact.nickname)
#         member_json['member_avatar'] = a_contact.avatar_url2
#         member_json_list.append(member_json)
#         wallet_json_list = list()
#         rows_wallet_list = db.session.query(CoinWalletMemberAddressRelate, CoinWalletQunMemberRelate) \
#             .outerjoin(CoinWalletQunMemberRelate,
#                        CoinWalletMemberAddressRelate.uqun_member_id == CoinWalletQunMemberRelate.uqun_member_id)\
#             .filter(CoinWalletMemberAddressRelate.wallet_is_deleted == 0,
#                     CoinWalletQunMemberRelate.member_username == a_contact.username).all()
#         member_json['wallet_count'] = len(rows_wallet_list)
#         for row_wallet in rows_wallet_list:
#             wallet = row_wallet[0]
#             wallet_json = dict()
#             wallet_json['wallet_id'] = wallet.wallet_id
#             wallet_json['coin_address'] = wallet.coin_address
#             wallet_json['is_origin'] = wallet.address_is_origin
#             wallet_json['last_updated_time'] = datetime_to_timestamp_utc_8(wallet.last_updated_time)
#             wallet_json_list.append(wallet_json)
#         member_json['wallets'] = wallet_json_list
#
#     return SUCCESS, member_json_list, total_count
#
#
# def get_members_without_coin_wallet(user_info, uqun_id = None, limit = 10, offset = 0):
#     filter_list_cw_qmr = list()
#     filter_list_cw_qmr.append(CoinWalletQunMemberRelate.member_is_deleted == 0)
#     filter_list_cw_qmr.append(CoinWalletQunMemberRelate.user_id == user_info.user_id)
#     if uqun_id is not None:
#         filter_list_cw_qmr.append(CoinWalletQunMemberRelate.uqun_id == uqun_id)
#     rows_member_username = db.session.query(CoinWalletQunMemberRelate.member_username).filter(*filter_list_cw_qmr).all()
#     members_has_wallet = {r[0] for r in rows_member_username}
#
#     status, member_json_list, total_count = get_members(user_info = user_info, uqun_id = uqun_id,
#                                                         limit = limit, offset = offset,
#                                                         member_username_except = members_has_wallet)
#
#     return status, member_json_list, total_count
#
#
# def get_members_coin_wallet_list(user_info, uqun_id = None, limit = 10, offset = 0):
#     members_coin_wallet_list = list()
#     filter_list_cw_qmr = list()
#     filter_list_cw_qmr.append(CoinWalletQunMemberRelate.member_is_deleted == 0)
#     filter_list_cw_qmr.append(CoinWalletQunMemberRelate.user_id == user_info.user_id)
#     if uqun_id is not None:
#         filter_list_cw_qmr.append(CoinWalletQunMemberRelate.uqun_id == uqun_id)
#
#     rows_member_username = db.session.query(CoinWalletQunMemberRelate.member_username,
#                                             func.max(CoinWalletQunMemberRelate.last_update_time),
#                                             AContact)\
#         .outerjoin(AContact, CoinWalletQunMemberRelate.member_username == AContact.username)\
#         .filter(*filter_list_cw_qmr)\
#         .group_by(CoinWalletQunMemberRelate.member_username)\
#         .order_by(func.max(CoinWalletQunMemberRelate.last_update_time)).limit(limit).offset(offset).all()
#
#     member_info_dict = dict()
#     member_username_list = list()
#     for row in rows_member_username:
#         member_username = row[0]
#         last_update_time = row[1]
#         a_contact = row[2]
#         member_info_json = dict()
#         member_info_json['member_id'] = -1
#         member_info_json['member_nickname'] = ""
#         member_info_json['member_avatar'] = ""
#         if a_contact:
#             member_info_json['member_id'] = a_contact.id
#             member_info_json['member_nickname'] = str_to_unicode(a_contact.nickname)
#             member_info_json['member_avatar'] = a_contact.avatar_url2
#         member_info_json['last_update_time'] = datetime_to_timestamp_utc_8(last_update_time)
#         member_info_dict[member_username] = member_info_json
#         member_username_list.append(member_username)
#
#     filter_list_wallet = list()
#     filter_list_wallet.append(CoinWalletQunMemberRelate.member_username.in_(member_username_list))
#     filter_list_wallet.append(CoinWalletMemberAddressRelate.wallet_is_deleted == 0)
#     if uqun_id is not None:
#         filter_list_wallet.append(CoinWalletQunMemberRelate.uqun_id == uqun_id)
#     rows_wallet_list = db.session.query(CoinWalletMemberAddressRelate, CoinWalletQunMemberRelate.member_username) \
#         .outerjoin(CoinWalletQunMemberRelate,
#                    CoinWalletMemberAddressRelate.uqun_member_id == CoinWalletQunMemberRelate.uqun_member_id)\
#         .filter(*filter_list_wallet).\
#         order_by(CoinWalletMemberAddressRelate.last_updated_time.desc()).all()
#
#     member_wallet_dict = dict()
#     for row in rows_wallet_list:
#         wallet = row[0]
#         wallet_json = dict()
#         wallet_json['wallet_id'] = wallet.wallet_id
#         wallet_json['coin_address'] = wallet.coin_address
#         wallet_json['is_origin'] = wallet.address_is_origin
#         wallet_json['last_updated_time'] = datetime_to_timestamp_utc_8(wallet.last_updated_time)
#         member_username = row[1]
#         member_wallet_dict.setdefault(member_username, list())
#         member_wallet_dict[member_username].append(wallet_json)
#
#     for member_username in member_username_list:
#         member_info_json = member_info_dict[member_username]
#         wallet_list = member_wallet_dict[member_username]
#         member_info_json['wallet_count'] = len(wallet_list)
#         member_info_json['wallets'] = wallet_list
#         members_coin_wallet_list.append(member_info_json)
#
#     return SUCCESS, members_coin_wallet_list


def check_whether_message_is_a_coin_wallet(a_message):
    """
    根据一条message，判断该条是否符合币的地址规则
    :param a_message:
    :return:
    """
    message_text = str_to_unicode(a_message.real_content).strip()
    # 此处正则为0x开头的由这些东西组成的从头到尾的字符串
    if re.match('^0x[0-9a-zA-Z]+$', message_text) and 6 <= len(message_text) < 250:
        _save_coin_wallet(a_message, message_text)
        return True
    else:
        fa = message_text.find(u"钱包#")
        if fa == -1:
            return False
        else:
            _save_coin_wallet(a_message, message_text[fa + 3:])
            return True


def _save_coin_wallet(a_message, wallet_address):
    chatroomname = a_message.talker
    username = a_message.real_talker
    a_chatroom = BaseModel.fetch_one(Chatroom, "nickname", where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
    if not a_chatroom:
        logger.error(u"没有找到该群的信息. chatroomname: %s." % chatroomname)
        return ERR_WRONG_ITEM
    chatroom_nick = a_chatroom.nickname
    uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
    client_id_set = set()
    for uqr in uqr_list:
        client_id_set.add(uqr.client_id)

    now_time = datetime_to_timestamp_utc_8(datetime.now())
    address_info = dict()
    address_info.setdefault("address", wallet_address)
    address_info.setdefault("create_time", now_time)
    address_info.setdefault("update_time", now_time)
    address_info.setdefault("is_deleted", 0)

    for client_id in client_id_set:
        wallet = BaseModel.fetch_one(Wallet, "*", where_clause = BaseModel.where_dict({"client_id": client_id,
                                                                                       "chatroomname": chatroomname,
                                                                                       "username": username,
                                                                                       "address": wallet_address}))
        if not wallet:
            wallet = CM(Wallet)
            wallet.client_id = client_id
            wallet.chatroomname = chatroomname
            wallet.chatroom_nick = chatroom_nick
            wallet.username = username
            wallet.address_count = 0
            wallet.create_time = now_time
            wallet.address = wallet_address

        wallet.is_deleted = 0
        wallet.update_time = now_time
        wallet.save()

    return SUCCESS


# def build_wallet_excel(user_info, uqun_id = None):
#
#     return ''
