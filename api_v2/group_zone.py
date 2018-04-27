# -*- coding: utf-8 -*-
from flask import request
from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import time

MSG_TYPE_UNKNOWN = -1  # 未知类型
MSG_TYPE_TXT = 1
MSG_TYPE_PIC = 3
MSG_TYPE_MP3 = 34
MSG_TYPE_NAME_CARD = 42
MSG_TYPE_MP4 = 43
MSG_TYPE_GIF = 47
MSG_TYPE_VIDEO = 62
MSG_TYPE_SHARE = 49
MSG_TYPE_SYS = 10000
MSG_TYPE_ENTERCHATROOM = 570425393

MSG_TYPE_DICK = {
    1: ['.txt', '.pdf', '.doc', '.xls'],
    2: [],
    3: ['.mp4', 'mov'],
    4: ['.png', '.jpg', '.jpeg']

}




@main_api_v2.route("/group_zone_lists", methods=['POST'])
def get_group_zone_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
        client_quns = [client_qun.to_json_full() for client_qun in client_quns]

    except:
        return make_response(ERR_WRONG_ITEM)

    try:
        for client_qun in client_quns:
            chatroom_info = BaseModel.fetch_one("a_chatroom", "*",
                                                where_clause=BaseModel.where_dict(
                                                    {"chatroomname": client_qun.get('chatroomname')}))

            # client_qun_to_dict = client_qun.to_json_full()
            client_qun.update(chatroom_info.to_json_full())

            # client_qun.nickname_real = chatroom_info.nickname_real if chatroom_info.nickname_real else None
            # client_qun.member_count = chatroom_info.member_count
    except:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, client_quns_list=client_quns)


@main_api_v2.route("/group_zone_sources", methods=['POST'])
def get_group_zone_sources():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
        client_quns = [client_qun.to_json_full() for client_qun in client_quns]
    except:
        return make_response(ERR_WRONG_ITEM)

    # 群id--talker
    talker = request.json.get('chatroomname')
    keyword = request.json.get('keyword')
    source_type = request.json.get('source_type')
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    order_type = request.json.get('order_type')

    # 获取所有的群空间
    # if not talker:
    #     messages = []
    #     for client_qun in client_quns:
    #         messages.extend(BaseModel.fetch_all('a_message', '*',
    #                                             where_clause=BaseModel.where_dict(
    #                                                {"talker": client_qun.get('chatroomname')}),
    #                                             page=page, pagesize=pagesize,
    #                                             order_by=BaseModel.order_by({"create_time": order_type})
    #                                             )
    #
    #                         )
    if talker:
        messages = BaseModel.fetch_all('a_message', '*',
                                       where_clause=BaseModel.where_dict(
                                            {"talker": talker}),
                                       page=page, pagesize=pagesize,
                                       order_by=BaseModel.order_by({"create_time": order_type})
                                       )

if __name__ == "__main__":

    BaseModel.extract_from_json()
    # messages = BaseModel.fetch_all("a_message", "*",
    #                                where_clause=BaseModel.where_dict(
    #                                    {"talker": '10973997003@chatroom',
    #                                     'create_time': 1524804656000}),
    #                                pagesize=10, page=1,
    #                                order_by=BaseModel.order_by({"create_time": "desc"})
    #                                )

    messages = BaseModel.fetch_all("a_message", "*",
                                   where_clause=BaseModel.or_(
                                       ['=', 'talker', '5663579223@chatroom'],
                                       ['=', 'talker', '10973997003@chatroom']
                                   ),
                                   pagesize=10, page=1,
                                   order_by=BaseModel.order_by({"create_time": "desc"})
                                   )
    # messages = BaseModel.fetch_all("a_message", "*")
    print [message.to_json_full() for message in messages].__len__()
    print messages.__len__()
    #
    # # messages = BaseModel.fetch_all('a_message', '*',
    # #                                where_clause=BaseModel.where_dict({"talker": 'wxid_zy8gemkhx2r222'}),
    # #                                pagesize=1, page=1)
    #
    # print hasattr(messages[0], 'update')
    # client_quns = BaseModel.fetch_all("client_qun_r", "*",
    #                                   where_clause=BaseModel.where_dict({"client_id": 2}))
    #
    # chatroom_info = BaseModel.fetch_one("a_chatroom", "*",
    #                                     where_clause=BaseModel.where_dict({"chatroomname": "8835992041@chatroom"}))
    #
    #
    # print client_quns
    pass