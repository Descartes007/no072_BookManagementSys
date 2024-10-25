#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/14 9:05
# Description: xxx
from flask import Blueprint, jsonify, request

from apps.audit.model import Audit
from exts import db
from exts.auth import require_access_token
from exts.logHandler import base_logger as logger

audit_bp = Blueprint('audit', __name__)
model_name = '审计管理'


# @audit_bp.route('/audit/add')
# def audit_add():
#     try:
#         col = Audit(op_ip=, op_user=, op_module=, op_event=)
#         db.session.add(col)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         logger.error("commit audit info fail")
#         logger.exception(e)


@audit_bp.route('/audit/query', methods=['POST'])
@require_access_token
def audit_query(current_user):
    info_list = []

    if len(request.get_json()) == 0:
        query_result = Audit.query.order_by(Audit.op_time.desc())
        pageTotal = len(query_result)
    else:
        if "query_string" in request.get_json():
            query_string = request.get_json()['query_string']
            # 指定分页信息查询数据
            if query_string == '':
                page = int(request.get_json()['page'])
                size = int(request.get_json()['size'])
                offset = (page - 1) * size
                query_result = Audit.query.order_by(Audit.op_time.desc()).offset(offset).limit(size).all()
                pageTotal = len(Audit.query.all())
        else:
            query_result=Audit.query.filter(Audit.op_time.between(request.get_json()['start_time'],request.get_json()['end_time'])).order_by(Audit.op_time.desc()).all()
            pageTotal = len(query_result)
    for i in query_result:
        obj = i.to_dict()
        data = {"id": obj['id'], "time": int(obj['op_time'].timestamp()), "ip": obj['op_ip'],
                "user": obj['op_user'],
                "model": obj['op_module'],
                "event": obj['op_event']}
        info_list.append(data)
    response = {"status": True, "message": "查询成功", "infos": info_list, "pageTotal": pageTotal}
    return jsonify(response)
