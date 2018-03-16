# -*- coding: utf-8 -*-

import logging
import re

from datetime import datetime

from configs.config import db, SUCCESS, ERR_WRONG_USER_ITEM
from models.coin_wallet_models import CoinWalletQunMemberRelate, CoinWalletMemberAddressRelate
from models.qun_friend_models import UserQunRelateInfo
from models.user_bot_models import UserInfo
from utils.u_transformat import str_to_unicode

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
