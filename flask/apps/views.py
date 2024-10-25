#!/usr/bin/env python3
# ! -*- coding=utf-8 -*-
'''
**************************************************************
** @Create：2024/2/27 15:32
** @Author：anonymous
** @Description： 全局路由，不属于任何app组件
**************************************************************
'''
import json
import re
import settings
from flask import Blueprint, request, jsonify, app
from exts.auth import require_access_token

global_bp = Blueprint('global', __name__)



# @global_bp.route('/audit/query', methods=['POST'])
# @require_access_token
# def audit_query(current_user):
#     info_list = []
#     id = 1
#     with open(settings.Config.LOG_BASE_DIR + '/audit.log', mode='r', encoding='utf-8', errors='ignore') as f:
#         for line in f.readlines():
#             line_infos = re.findall('\[(.*?)\]', line)
#             if len(line_infos)!=5:
#                 continue
#             else:
#                 data = {"id": id, "time": line_infos[0],  "ip": line_infos[1], "user": line_infos[2], "model": line_infos[3],
#                         "event": line_infos[4]}
#                 id += 1
#                 info_list.append(data)
#     pageTotal = len(info_list)
#     if len(request.get_json()) == 0:
#         response = {"status": True, "message": "查询成功", "infos": info_list, "pageTotal": pageTotal}
#     else:
#         if "query_string" in request.get_json():
#             query_string = request.get_json()['query_string']
#             # 指定分页信息查询数据
#             if query_string == '':
#                 page = int(request.get_json()['page'])
#                 size = int(request.get_json()['size'])
#                 offset = (page - 1) * size
#                 data = info_list[offset:page * size:1]
#                 response = {"status": True, "message": "查询成功", "infos": data, "pageTotal": pageTotal}
#     return jsonify(response)
