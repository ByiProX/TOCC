# -*- coding: utf-8 -*-
from flask import request
from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response


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
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    try:
        for client_qun in client_quns:
            chatroom_info = BaseModel.fetch_all("a_chatroom", "*",
                                                where_clause=BaseModel.where_dict(
                                                    {"chatroomname": client_qun.get('chatroomname')}))[0]
            client_qun.update(chatroom_info.to_json_full())
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, client_quns_list=client_quns)


@main_api_v2.route("/count_sources", methods=['POST'])
def get_count_sources():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    client_quns_name_list = [client_qun.chatroomname for client_qun in client_quns]

    count_dict = dict()
    for i in range(2, 8):
        num = BaseModel.count("a_message",
                              where_clause=BaseModel.and_(
                                  ["in", "talker", client_quns_name_list],
                                  ["=", "real_type", i]))
        count_dict[i] = num

    return make_response(SUCCESS, count=count_dict)


@main_api_v2.route("/group_zone_sources", methods=['POST'])
def get_group_zone_sources():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    print client_id
    talker = request.json.get('chatroomname')
    keyword = request.json.get('keyword', '')
    real_type = request.json.get('real_type')
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    order_type = request.json.get('order_type', 'desc')

    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    if not talker:
        client_quns_name_list = [client_qun.chatroomname for client_qun in client_quns]
    else:
        client_quns_name_list = [talker]

    if not real_type:
        real_type_list = [i for i in range(2, 8)]
    else:
        real_type_list = [real_type]

    print ":::::", client_quns_name_list
    sources = BaseModel.fetch_all('a_message', ['bot_username', 'create_time',
                                                'msg_local_id', 'real_type',
                                                'thumb_url', 'source_url',
                                                'title', 'desc',
                                                'size', 'duration',
                                                'talker', 'real_talker'],
                                  where_clause=BaseModel.and_(
                                      ['in', 'talker', client_quns_name_list],
                                      ['in', 'real_type', real_type_list],
                                      # ['=', 'type', source_type],
                                      # ['in', 'type', [49, 3, 436207665, 1]],
                                      ['like', 'title', keyword]),
                                  page=page, pagesize=pagesize,
                                  order_by=BaseModel.order_by({"create_time": order_type})
                                  )
    total_count = len(sources)
    sources = [source.to_json() for source in sources]
    # print '::::::::::::::::::::::::::::aa', sources.__len__()
    # print sources

    try:
        for source in sources:
            chatroom_info = BaseModel.fetch_all('a_chatroom', ['avatar_url', 'chatroomname',
                                                               'nickname', 'nickname_real',
                                                               'member_count'],
                                                where_clause=BaseModel.where_dict(
                                                    {"chatroomname": source.get("talker")}
                                                ))[0]
            source["chatroom_info"] = chatroom_info.to_json()

            client_info = BaseModel.fetch_all('a_contact', ['avatar_url', 'nickname', 'username'],
                                              where_clause=BaseModel.where_dict(
                                                  {"username": source.get("real_talker")}
                                              ))[0]

            source["client_info"] = client_info.to_json()

        # print '::::::::::::::::::::::::::::bb'
        # print sources
        return make_response(SUCCESS, sources=sources, total_count=total_count)
    except Exception:
        return make_response(ERR_WRONG_ITEM)


if __name__ == "__main__":
    BaseModel.extract_from_json()

    c = BaseModel.count("a_message",
                        where_clause=BaseModel.and_(
                            ["in", "talker", ['10973997003@chatroom', '5663579223@chatroom']],
                            ["=", "real_type", 5]))

    print c

    messages = BaseModel.fetch_all("a_message", ['bot_username', 'create_time',
                                                 'msg_local_id', 'real_type',
                                                 'thumb_url', 'source_url',
                                                 'title', 'desc',
                                                 'size', 'duration'],
                                   where_clause=
                                   BaseModel.and_(
                                       ['in', 'talker', ['10973997003@chatroom', '5663579223@chatroom']],
                                       ['like', 'real_content', ''],
                                       ['=', 'real_type', 1],
                                   ),

                                   pagesize=10, page=1,
                                   order_by=BaseModel.order_by({"create_time": "desc"})
                                   )

    # print messages[0].to_json()

    # ms = BaseModel.fetch_all("a_message", "*",
    #                          # where_clause=
    #                          # BaseModel.and_(
    #                          #     ['in', 'talker', ['10973997003@chatroom', '5663579223@chatroom']],
    #                          #     ['like', 'real_content', ''],
    #                          #     ['in', 'type', [49, 3]],
    #                          # ),
    #
    #                          pagesize=10, page=1,
    #                          order_by=BaseModel.order_by({"create_time": "desc"})
    #                          )
    # ms = [m.to_json_full() for m in ms]
    #
    # cs = BaseModel.fetch_all("client_member", "*",
    #                          # where_clause=
    #                          # BaseModel.and_(
    #                          #     ['in', 'talker', ['10973997003@chatroom', '5663579223@chatroom']],
    #                          #     ['like', 'real_content', ''],
    #                          #     ['in', 'type', [49, 3]],
    #                          # ),
    #
    #                          pagesize=10, page=1,
    #                          order_by=BaseModel.order_by({"create_time": "desc"})
    #                          )
    # cs = [c.to_json_full() for c in cs]

    # messages = BaseModel.fetch_all("a_message", "*")
    # print [message.to_json_full() for message in messages][2]
    # print messages[0].talker
    # print messages.__len__()
    # print [m['type'] for m in ms]
    # print cs.__len__()
    #
    # for c in cs:
    #     c.update({'a': 11111111111111111111111111111})
    # print cs.__len__()
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

    tasks = BaseModel.fetch_all("batch_send_task", "*")
    print tasks[0].client_id


    pass
