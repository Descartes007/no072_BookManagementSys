#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/10 10:46
# Description: xxx


import json
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from apps.author.model import Author
from apps.book.model import *
from apps.publish.model import Publisher
from exts.auth import require_access_token
from exts.common import insert_audit_log
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger

author_bp = Blueprint('author', __name__)
model_name = '作者管理'


@author_bp.route('/author/add', methods=['POST'])
@require_access_token
def author_add(current_user):
    # 查询条目是否存在
    college = Author.query.filter_by(name=request.get_json()["name"]).first()
    if college is None:
        max_id_query = db.session.query(func.max(Author.id)).scalar()
        if max_id_query is None:
            max_id = 0
        else:
            max_id = max_id_query
        try:
            col = Author(author_id=max_id + 1, name=request.get_json()["name"])
            db.session.add(col)  # 添加一条
            # 提交事务
            db.session.commit()
            response = {"code": 0, "id": max_id + 1, "message": "创建成功!", "status": True}
            # audit_logger.debug(
            #     "[{0}] [{1}] [{2}] [添加信息: {3}]".format(request.remote_addr, current_user, model_name,
            #                                                request.get_json()["name"]))
            insert_audit_log(request.remote_addr, current_user, model_name, '添加信息: '+request.get_json()["name"])
        except Exception as e:
            logger.exception(e)
            logger.error("commit author info fail")
            response = {"code": -1, "message": "创建失败!", "status": False}
    else:
        logger.error("add author info fail, info is exist")
        response = {"code": -1, "message": "条目已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@author_bp.route('/author/query', methods=['POST'])
@require_access_token
def author_query(current_user):
    authors_list = []
    pageTotal = len(Author.query.all())
    if len(request.get_json()) == 0:
        query_result = Author.query.all()
    else:

        query_string = request.get_json()['query_string']
        # 指定分页信息查询数据
        if query_string == '':
            page = int(request.get_json()['page'])
            size = int(request.get_json()['size'])
            offset = (page - 1) * size
            query_result = Author.query.offset(offset).limit(size).all()
        else:
            query_result = Author.query.filter((Author.name.contains(query_string))).all()
    for i in query_result:
        author = dict(i)
        # 通过专业反向关联查询学院名称
        # 方式一   speciality['college']=College.query.get(i.college).name
        authors_list.append(author)
    response = {"status": True, "message": "查询成功", "infos": authors_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@author_bp.route('/author/count', methods=['POST'])
@require_access_token
def author_count(current_user):
    count = len(Author.query.all())
    response = {"status": True, "message": "统计成功", "count": count}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@author_bp.route('/author/update', methods=['POST'])
@require_access_token
def author_update(current_user):
    try:
        spe_obj = Author.query.filter_by(name=request.get_json()["name"])
        spe_obj.update({'name': request.get_json()["name"]})
        # 提交更新到数据库（事务提交）
        db.session.commit()
        response = {"code": 0, "message": "保存成功!", "status": True}
        # audit_logger.debug(
        #     "[{0}] [{1}] [{2}] [更新信息: {3}]".format(request.remote_addr, current_user, model_name,
        #                                                request.get_json()["name"]))
        insert_audit_log(request.remote_addr, current_user, model_name, '更新信息: ' + request.get_json()["name"])
    except Exception as e:
        logger.exception(e)
        db.session.rollback()
        logger.error("update author info fail")
        response = {"code": -1, "message": "保存失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@author_bp.route('/author/delete', methods=['POST'])
@require_access_token
def author_delete(current_user):
    failed_item_ids = []
    if not isinstance(request.get_json()["id"], list):
        delete_ids = [request.get_json()["id"]]
    else:
        delete_ids = request.get_json()["id"]
    for speciality_id in delete_ids:
        query_speciality = Author.query.get(speciality_id)
        # 判断该条目是否存在
        if query_speciality is None:
            logger.error("delete {0} from table author fail".format(request.get_json()))
            failed_item_ids.append(speciality_id)
        else:
            try:
                db.session.delete(query_speciality)  # 将对象放在缓存中准备删除
                db.session.commit()  # 提交事务，删除
                logger.success("delete {0} from table author success".format(request.get_json()))
                # audit_logger.debug(
                #     "[{0}] [{1}] [{2}] [删除信息: {3}]".format(request.remote_addr, current_user, model_name,
                #                                                query_speciality.name))
                insert_audit_log(request.remote_addr, current_user, model_name,'删除信息: ' + query_speciality.name)
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                failed_item_ids.append(speciality_id)
                logger.error("delete {0}  from table author fail".format(request.get_json()))
    if len(failed_item_ids) == 0:
        response = {"status": "success", "code": 0, "message": '删除成功'}
    elif len(failed_item_ids) == len(delete_ids):
        response = {"status": "fail", "code": -2, "message": '删除失败'}
    else:
        response = {"status": "success", "code": -1, "message": '部分条目删除失败'}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)
