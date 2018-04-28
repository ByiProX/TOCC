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

MSG_TYPE_DICT = {
    1: ['.txt', '.pdf', '.doc', '.xls'],
    2: ['http://', 'https://'],
    3: ['.mp4', 'mov'],
    4: ['.png', '.jpg', '.jpeg', '.gif']

}

# def get_source_type(type, real_content):




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
            chatroom_info = BaseModel.fetch_all("a_chatroom", "*",
                                                where_clause=BaseModel.where_dict(
                                                    {"chatroomname": client_qun.get('chatroomname')}))[0]
            client_qun.update(chatroom_info.to_json_full())
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
    talker = request.json.get('chatroomname')
    keyword = request.json.get('keyword')
    source_type = request.json.get('source_type')
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    order_type = request.json.get('order_type', 'desc')

    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
    except:
        return make_response(ERR_WRONG_ITEM)

    if not talker:
        client_quns_name_list = [client_qun.chatroomname for client_qun in client_quns]
    else:
        client_quns_name_list = [talker]

    sources = BaseModel.fetch_all('a_message', '*',
                                  where_clause=BaseModel.and_(
                                      ['in', 'talker', client_quns_name_list],
                                      ['in', 'type', [43, 1]],
                                      ['like', 'real_content', keyword]),
                                  page=page, pagesize=pagesize,
                                  order_by=BaseModel.order_by({"create_time": order_type})
                                  )
    sources = [source.to_json_full() for source in sources]

    for source in sources:
        chatroom_info = BaseModel.fetch_all('a_chatroom', '*',
                                            where_clause=BaseModel.where_dict(
                                                {"chatroomname": source.talker}
                                            ))[0]
        source.update(chatroom_info.to_json_full())

    return make_response(SUCCESS, sources=sources)


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
                                   where_clause=
                                   BaseModel.and_(
                                       ['=', 'talker', '10973997003@chatroom'],
                                       ['like', 'real_content', ''],
                                       ['=', 'type', 49],
                                   ),

                                   pagesize=10, page=1,
                                   order_by=BaseModel.order_by({"create_time": "desc"})
                                   )

    # messages = BaseModel.fetch_all("a_message", "*")
    # print [message.to_json_full() for message in messages][2]
    # print messages[0].talker
    print messages
    # a = BaseModel.fetch_all("a_chatroom", "*", where_clause=BaseModel.where_dict({"chatroomname": '8835992041@chatroom'}))
    # print a[0].chatroomname

    # print messages[1].real_content
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

    # print BaseModel.fetch_all("a_chatroom", "*",
    #                           where_clause=BaseModel.where_dict(
    #                               {"chatroomname": '8835992041@chatroom'}))[0].to_json_full()
    #
    # BaseModel.fetch_all('a_message', '*',
    #                     where_clause=BaseModel.where_dict(
    #                         {"talker": client_qun.get('chatroomname')}),
    #                     page=page, pagesize=pagesize,
    #                     order_by=BaseModel.order_by({"create_time": order_type})
    #                     )

    pass
