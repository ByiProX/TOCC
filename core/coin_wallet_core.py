# -*- coding: utf-8 -*-

import logging
import re

from datetime import datetime

from configs.config import db, SUCCESS, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM
from models.android_db_models import AContact, AMember
from models.coin_wallet_models import CoinWalletQunMemberRelate, CoinWalletMemberAddressRelate
from models.qun_friend_models import UserQunRelateInfo
from models.user_bot_models import UserInfo
from utils.u_time import datetime_to_timestamp_utc_8
from utils.u_transformat import str_to_unicode, unicode_to_str

logger = logging.getLogger('main')


def switch_func_coin_wallet(user_info, switch):
    """
    打开或关闭钱包记录查看功能
    :param user_info:
    :param switch:
    :return:
    """
    if user_info.func_coin_wallet and switch:
        logger.error("目前已为开启状态，无需再次开启. 返回正常.")
        return SUCCESS
    if not user_info.func_coin_wallet and not switch:
        logger.error("目前已为关闭状态，无需再次关闭. 返回正常.")
        return SUCCESS

    user_info.func_coin_wallet = switch
    db.session.merge(user_info)
    db.session.commit()
    return SUCCESS


# def get_coin_wallet_setting(user_info):
#     """
#     得到一个人的所有自动回复设置
#     :return:
#     """
#     ar_setting_info_list = db.session.query(AutoReplySettingInfo).filter(
#         AutoReplySettingInfo.user_id == user_info.user_id).filter(AutoReplySettingInfo.is_deleted == 0).order_by(
#         AutoReplySettingInfo.setting_create_time.desc()).all()
#
#     result = []
#     for ar_setting_info in ar_setting_info_list:
#         status, task_detail_res = get_setting_detail(ar_setting_info)
#         if status == SUCCESS:
#             result.append(deepcopy(task_detail_res))
#         else:
#             logger.error(u"部分任务无法读取. setting_id: %s." % ar_setting_info.setting_id)
#     return SUCCESS, result

def get_members(user_info, uqun_id = None, limit = 10, offset = 0, member_username_except = None, keyword = None):
    filter_list_members = list()
    if keyword:
        filter_list_members.append(AContact.nickname.like('' + unicode_to_str(keyword) + ''))
    if member_username_except:
        filter_list_members.append(AMember.username.notin_(member_username_except))
    if uqun_id is not None:
        filter_list_members.append(UserQunRelateInfo.uqun_id == uqun_id)
    else:
        filter_list_members.append(UserQunRelateInfo.user_id == user_info.user_id)

    members_query = db.session.query(UserQunRelateInfo.uqun_id, AContact) \
        .outerjoin(AMember, UserQunRelateInfo.chatroomname == AMember.chatroomname) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_members)
    total_count = members_query.count()
    rows = members_query.limit(limit).offset(offset).all()

    member_json_list = list()
    for row in rows:
        uqun_id = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json['chatroom_id'] = uqun_id
        member_json['member_id'] = a_contact.id
        member_json['member_nickname'] = str_to_unicode(a_contact.nickname)
        member_json['member_avatar'] = a_contact.avatar_url2
        member_json_list.append(member_json)
        wallet_json_list = list()
        wallet_list = db.session.query(CoinWalletQunMemberRelate, CoinWalletMemberAddressRelate) \
            .outerjoin(CoinWalletMemberAddressRelate,
                       CoinWalletQunMemberRelate.uqun_member_id == CoinWalletMemberAddressRelate.uqun_member_id)\
            .filter(CoinWalletMemberAddressRelate.wallet_is_deleted == 0,
                    CoinWalletQunMemberRelate.member_username == a_contact.username).all()
        member_json['wallet_count'] = len(wallet_list)
        for wallet in wallet_list:
            wallet_json = dict()
            wallet_json['wallet_id'] = wallet.wallet_id
            wallet_json['coin_address'] = wallet.coin_address
            wallet_json['is_origin'] = wallet.address_is_origin
            wallet_json['last_updated_time'] = datetime_to_timestamp_utc_8(wallet.last_updated_time)
            wallet_json_list.append(wallet_json)

    return SUCCESS, member_json_list, total_count


def get_members_without_coin_wallet(user_info, uqun_id = None, limit = 10, offset = 0):
    filter_list_cw_qmr = list()
    filter_list_cw_qmr.append(CoinWalletQunMemberRelate.member_is_deleted == 0)
    filter_list_cw_qmr.append(CoinWalletQunMemberRelate.user_id == user_info.user_id)
    if uqun_id is not None:
        filter_list_cw_qmr.append(CoinWalletQunMemberRelate.uqun_id == uqun_id)
    rows_member_username = db.session.query(CoinWalletQunMemberRelate.member_username).filter(*filter_list_cw_qmr).all()
    members_has_wallet = {r[0] for r in rows_member_username}

    status, member_json_list, total_count = get_members(user_info = user_info, uqun_id = uqun_id,
                                                        limit = limit, offset = offset,
                                                        member_username_except = members_has_wallet)

    return status, member_json_list, total_count


def get_members_coin_wallet_list(user_info, uqun_id = None, limit = 10, offset = 0):
    members_coin_wallet_list = list()
    filter_list_cw_qmr = list()
    filter_list_cw_qmr.append(CoinWalletQunMemberRelate.member_is_deleted == 0)
    filter_list_cw_qmr.append(CoinWalletQunMemberRelate.user_id == user_info.user_id)
    if uqun_id is not None:
        filter_list_cw_qmr.append(CoinWalletQunMemberRelate.uqun_id == uqun_id)
    cw_qmr_list = db.session.query(CoinWalletQunMemberRelate, AContact)\
        .outerjoin(UserQunRelateInfo, CoinWalletQunMemberRelate.member_username == AContact.username)\
        .filter(*filter_list_cw_qmr)\
        .order_by(CoinWalletQunMemberRelate.last_update_time.desc()).limit(limit).offset(offset).all()

    for row in cw_qmr_list:
        cw_qmr = row[0]
        a_contact = row[1]
        cw_qmr_json = dict()
        # 暂：member_id = AContact.id
        cw_qmr_json['member_id'] = -1
        cw_qmr_json['member_nickname'] = ""
        cw_qmr_json['member_avatar'] = ""
        if a_contact:
            cw_qmr_json['member_id'] = a_contact.id
            cw_qmr_json['member_nickname'] = str_to_unicode(a_contact.nickname)
            cw_qmr_json['member_avatar'] = a_contact.avatar_url2
        cw_qmr_json['chatroom_id'] = cw_qmr.uqun_id
        cw_qmr_json['last_update_time'] = datetime_to_timestamp_utc_8(cw_qmr.last_update_time)
        wallet_json_list = list()
        wallet_list = db.session.query(CoinWalletMemberAddressRelate)\
            .filter(CoinWalletMemberAddressRelate.uqun_member_id == cw_qmr.uqun_member_id,
                    CoinWalletMemberAddressRelate.wallet_is_deleted == 0).all()
        cw_qmr_json['wallet_count'] = len(wallet_list)
        for wallet in wallet_list:
            wallet_json = dict()
            wallet_json['wallet_id'] = wallet.wallet_id
            wallet_json['coin_address'] = wallet.coin_address
            wallet_json['is_origin'] = wallet.address_is_origin
            wallet_json['last_updated_time'] = datetime_to_timestamp_utc_8(wallet.last_updated_time)
            wallet_json_list.append(wallet_json)

    return SUCCESS, members_coin_wallet_list


def check_whether_message_is_a_coin_wallet(message_analysis):
    """
    根据一条message，判断该条是否符合币的地址规则
    :param message_analysis:
    :return:
    """
    message_text = str_to_unicode(message_analysis.real_content).strip()
    # 此处正则为0x开头的由这些东西组成的从头到尾的字符串
    if re.match('^0x[0-9a-zA-Z]+$', message_text) and 6 <= len(message_text) < 250:
        _save_coin_wallet(message_analysis, message_text)
        return True
    else:
        fa = message_text.find(u"钱包#")
        if fa == -1:
            return False
        else:
            _save_coin_wallet(message_analysis, message_text[fa + 3:])
            return True


def _save_coin_wallet(message_analysis, wallet_address):
    message_chatroomname = message_analysis.talker
    member_username = message_analysis.real_talker

    uqr_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.chatroomname == message_chatroomname,
                                                               UserQunRelateInfo.is_deleted == 0).all()
    for uqr_info in uqr_info_list:
        uqun_id = uqr_info.uqun_id

        user_id = uqr_info.user_id
        user_info = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        if not user_info:
            logger.error(u"没有找到uqr绑定关系的userinfo. uqun_id: %s." % uqun_id)
            return ERR_WRONG_USER_ITEM
        # 用户功能关闭，不对其进行记录
        if user_info.func_coin_wallet is False:
            continue

        old_cw_qmr_info = db.session.query(CoinWalletQunMemberRelate). \
            filter(CoinWalletQunMemberRelate.uqun_id == uqun_id,
                   CoinWalletQunMemberRelate.member_username == member_username).first()
        # 之前有过存储
        if old_cw_qmr_info:
            old_cw_qmr_info.last_update_time = datetime.now()
            db.session.merge(old_cw_qmr_info)
            db.session.commit()
            uqun_member_id = old_cw_qmr_info.uqun_member_id
        # 之前没有该人
        else:
            cw_qmr_info = CoinWalletQunMemberRelate()
            cw_qmr_info.user_id = uqr_info.user_id
            cw_qmr_info.uqun_id = uqr_info.uqun_id
            cw_qmr_info.member_username = message_analysis.real_talker
            cw_qmr_info.member_is_deleted = False
            cw_qmr_info.last_update_time = datetime.now()
            db.session.add(cw_qmr_info)
            db.session.commit()
            uqun_member_id = cw_qmr_info.uqun_member_id

        cw_mar_info = CoinWalletMemberAddressRelate()
        cw_mar_info.uqun_member_id = uqun_member_id
        cw_mar_info.coin_address = wallet_address
        cw_mar_info.address_is_origin = True
        cw_mar_info.wallet_is_deleted = False
        cw_mar_info.found_in_qun_time = message_analysis.create_time
        cw_mar_info.last_updated_time = datetime.now()
        db.session.add(cw_mar_info)
        db.session.commit()

    return SUCCESS


def update_coin_address_by_id(wallet_id, address_text):
    wallet = db.session.query(CoinWalletMemberAddressRelate)\
        .filter(CoinWalletMemberAddressRelate.wallet_id == wallet_id).first()
    if wallet:
        wallet.coin_address = address_text
        db.session.commit()
        return SUCCESS
    else:
        return ERR_WRONG_ITEM


def delete_wallet_by_id(wallet_id):
    wallet = db.session.query(CoinWalletMemberAddressRelate)\
        .filter(CoinWalletMemberAddressRelate.wallet_id == wallet_id).first()
    if wallet:
        wallet.wallet_is_deleted = True
        # TODO: check and update for querying for non-wallet members
        # cw_qmr = db.session.query(CoinWalletQunMemberRelate)\
        #     .filter(CoinWalletQunMemberRelate.uqun_member_id == wallet.uqun_member_id).first()
        db.session.commit()
        return SUCCESS
    else:
        return ERR_WRONG_ITEM
