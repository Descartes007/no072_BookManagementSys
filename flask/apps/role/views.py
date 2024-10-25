#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/1 23:05
# Description: xxx

import json
from exts import db
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from apps.role.model import Role
from apps.book.model import *
from exts.auth import require_access_token
from exts.common import insert_audit_log
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger

role_bp = Blueprint('role', __name__)

model_name = '角色管理'


@role_bp.route('/role/add', methods=['POST'])
@require_access_token
def role_add(current_user):
    # 查询条目是否存在
    permission_result = Role.query.filter_by(name=request.get_json()["name"]).first()
    if permission_result is None:
        max_id_query = db.session.query(func.max(Role.id)).scalar()
        if max_id_query is None:
            max_id = 0
        else:
            max_id = max_id_query
        try:
            role_id = max_id + 1
            col = Role(role_id=role_id, name=request.get_json()["name"])
            db.session.add(col)  # 添加一条
            # 提交事务
            db.session.commit()
            response = {"code": 0, "id": role_id, "message": "添加成功!", "status": True}
            # audit_logger.debug("[{0}] [{1}] [{2}] [添加信息: {3}]".format(request.remote_addr, current_user,model_name, request.get_json()["name"]))
            insert_audit_log(request.remote_addr, current_user, model_name, '添加信息: ' + request.get_json()["name"])
        except Exception as e:
            logger.error("commit role info fail")
            logger.exception(e)
            response = {"code": -1, "message": "添加失败!", "status": False}
    else:
        logger.error("add role info fail, info is exist")
        response = {"code": -1, "message": "条目已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@role_bp.route('/role/query', methods=['POST'])
@require_access_token
def role_query(current_user):
    roles_list = []
    pageTotal = len(Role.query.all())
    if len(request.get_json()) == 0:
        query_result = Role.query.all()
    else:
        if request.get_json().get("id") is None:
            query_string = request.get_json()['query_string']
            # 指定分页信息查询数据
            if query_string == '':
                page = int(request.get_json()['page'])
                size = int(request.get_json()['size'])
                offset = (page - 1) * size
                query_result = Role.query.offset(offset).limit(size).all()
            else:
                query_result = Role.query.filter(Role.name.contains(query_string)).all()
        else:
            # 查询指定用户的权限
            query_result = Role.query.filter_by(id=request.get_json()['id']).all()
    for i in query_result:
        roles_dict = dict(i)
        old_list = roles_dict["permission_ids"].split(",")
        roles_dict.update({"permission_ids": [x for i, x in enumerate(old_list) if x not in old_list[:i]]})
        roles_list.append(roles_dict)
    response = {"status": True, "message": "查询成功", "infos": roles_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@role_bp.route('/role/update', methods=['POST'])
@require_access_token
def role_update(current_user):
    try:
        role_obj = Role.query.filter_by(id=request.get_json()["id"])
        role_obj.update({'permission_ids': ','.join(i for i in request.get_json()["permission_ids"])})
        # 提交更新到数据库（事务提交）
        db.session.commit()
        response = {"code": 0, "message": "保存成功!", "status": True}
        # audit_logger.debug("[{0}] [{1}] [{2}] [更新信息: {3}]".format(request.remote_addr, current_user, model_name, role_obj.first().name))
        insert_audit_log(request.remote_addr, current_user, model_name, '更新信息: ' + role_obj.first().name)
    except Exception as e:
        logger.exception(e)
        db.session.rollback()
        logger.error("update role info fail")
        response = {"code": -1, "message": "保存失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@role_bp.route('/role/delete', methods=['POST'])
@require_access_token
def user_delete(current_user):
    failed_item_ids = []
    if not isinstance(request.get_json()["id"], list):
        delete_ids = [request.get_json()["id"]]
    else:
        delete_ids = request.get_json()["id"]
    for role_id in delete_ids:
        query_result = Role.query.get(role_id)
        # 判断该条目是否存在
        if query_result is None:
            logger.error("delete {0} from table role fail".format(request.get_json()))
            failed_item_ids.append(role_id)
        else:
            try:
                db.session.delete(query_result)  # 将对象放在缓存中准备删除
                db.session.commit()  # 提交事务，删除
                logger.success("delete {0} from table role success".format(request.get_json()))
                # audit_logger.debug("[{0}] [{1}] [{2}] [删除信息: {3}]".format(request.remote_addr, current_user,model_name, query_result.name))
                insert_audit_log(request.remote_addr, current_user, model_name, '删除信息: ' + query_result.name)
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                failed_item_ids.append(role_id)
                logger.error("delete {0}  from table role fail".format(request.get_json()))
    if len(failed_item_ids) == 0:
        response = {"status": "success", "code": 0, "message": '删除成功'}
    elif len(failed_item_ids) == len(request.get_json()["id"]):
        response = {"status": "fail", "code": -2, "message": '删除失败'}
    else:
        response = {"status": "success", "code": -1, "message": '部分条目删除失败'}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)
