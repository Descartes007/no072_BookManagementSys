#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/2/28 17:24
# Description: xxx
import hashlib
import json
import os
import random
from datetime import timedelta
import pandas as pd
from flask import Blueprint, request, jsonify, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, func, and_
from werkzeug.utils import secure_filename, redirect
import settings
from apps.User.model import User
from apps.audit.model import Audit
from apps.author.model import Author
from apps.book.model import *
from apps.classification.model import Classification
from apps.publish.model import Publisher
from exts.auth import require_access_token
from exts.common import insert_audit_log
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger

book_bp = Blueprint('book', __name__)

model_name = '图书管理'


@book_bp.route('/entry/add', methods=['POST'])
@require_access_token
def book_add(current_user):
    # 查询条目是否存在
    stu = Book.query.filter_by(isbn_number=request.get_json()["isbn_number"]).first()
    if stu is None:
        max_id_query = db.session.query(func.max(Book.id)).scalar()
        if max_id_query is None:
            max_id = 10000
        else:
            max_id = max_id_query
        try:
            new_book = Book(book_id=max_id + 1, name=request.get_json()["name"],
                            isbn_number=request.get_json()["isbn_number"],
                            publishing=request.get_json()["publishing"], author=request.get_json()["author"],
                            publish_time=request.get_json()["publish_time"],
                            book_type=request.get_json()["book_type"],
                            book_price=request.get_json()["book_price"],
                            book_status=request.get_json()["status"],
                            inbound_time=datetime.now())
            db.session.add(new_book)  # 添加一条
            if request.get_json()["description"]:
                new_book.description = request.get_json()["description"]
            # 提交事务
            db.session.commit()
            response = {"code": 0, "id": max_id + 1, "message": "录入成功!", "status": True}
            insert_audit_log(request.remote_addr, current_user, model_name, '添加图书: ' + request.get_json()['name'])
        except Exception as e:
            logger.exception(e)
            logger.error("commit book info fail")
            response = {"code": -1, "message": "录入失败!", "status": False}
    else:
        logger.error("add book info fail, info is exist")
        response = {"code": -1, "message": "条目已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/entry/query', methods=['POST'])
@require_access_token
def entry_query(current_user):
    query_list = []
    if 'query_string' in request.get_json():
        query_string = request.get_json()['query_string']
        # 指定分页信息查询数据
        if query_string == '':
            page = int(request.get_json()['page'])
            size = int(request.get_json()['size'])
            offset = (page - 1) * size
            pageTotal = len(Book.query.all())
            query_result = Book.query.offset(offset).limit(size).all()
        # 指定关键字查询
        else:
            query_result = Book.query.filter(
                or_(Book.name.contains(query_string), Book.publishing.contains(query_string))).all()

    else:
        # 初始化查询条件列表
        query_conditions = []

        # 根据json_data中的字段构建查询条件
        if request.get_json()['bookname'] != '':
            query_conditions.append(Book.name.contains(request.get_json()['bookname']))
        if request.get_json()['publisher'] != '':
            query_conditions.append(Book.publishing == request.get_json()['publisher'])
        if request.get_json()['author'] != '':
            query_conditions.append(Book.author == request.get_json()['author'])
        if request.get_json()['status'] != '':
            query_conditions.append(Book.book_status == request.get_json()['status'])
            # 如果query_conditions为空，说明没有提供任何查询条件，可以决定返回一个空列表或执行其他操作
        if not query_conditions:
            query_result = []  # 或者可以抛出错误，或者返回所有书籍等
        else:
            # 使用and_连接所有查询条件，并执行查询
            query_result = Book.query.filter(and_(*query_conditions)).all()
        pageTotal = len(query_result)
    for i in query_result:
        book = dict(i)
        # 通过书籍反向关联查询出版社和作者名称
        book['publishing'] = i.backref_publisher.name
        book['author'] = i.backref_author.name
        book['book_type'] = i.backref_classification.type_name
        book['publish_time'] = int(dict(i)['publish_time'].timestamp())
        book['inbound_time'] = int(dict(i)['inbound_time'].timestamp())
        if i.outbound_time is not None:
            book['outbound_time'] = int(dict(i)['outbound_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.expire_time is not None:
            book['expire_time'] = int(dict(i)['expire_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.photo:
            photo_addr = 'http://' + settings.Config.SERVER_IP + ":" + str(settings.Config.SERVER_PORT) + i.photo
        else:
            photo_addr = ''

        book['photo'] = photo_addr
        # 把图书的借阅归还历史记录返回给前端
        borrow_history_results = Audit.query.filter(Audit.op_event.contains('借阅图书: ' + book['name'])).all()
        return_history_results = Audit.query.filter(Audit.op_event.contains('归还图书: ' + book['name'])).all()
        book.update({"borrow_history": []})
        if len(borrow_history_results) > 0:
            for result in borrow_history_results:
                book["borrow_history"].append(
                    {"time": int(result.op_time.timestamp()), "user": result.op_user, "event": "借阅图书"})
        if len(return_history_results) > 0:
            for result in return_history_results:
                book["borrow_history"].append(
                    {"time": int(result.op_time.timestamp()), "user": result.op_user, "event": "归还图书"})
        query_list.append(book)
    response = {"status": True, "message": "查询成功", "infos": query_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)

@book_bp.route('/entry/detail', methods=['POST'])
@book_bp.route('/book/query', methods=['POST'])
@require_access_token
def book_query(current_user):
    query_list = []
    if 'query_string' in request.get_json():
        query_string = request.get_json()['query_string']
        # 指定分页信息查询数据
        if query_string == '':
            page = int(request.get_json()['page'])
            size = int(request.get_json()['size'])
            offset = (page - 1) * size
            pageTotal = len(Book.query.filter_by(book_status=0).all())
            query_result = Book.query.filter_by(book_status=0).offset(offset).limit(size).all()
        # 指定关键字查询
        else:
            query_result = Book.query.filter(
                or_(Book.name.contains(query_string), Book.publishing.contains(query_string))).all()
    elif 'rd_num' in request.get_json():
        # 查询所有条目
        query_result = Book.query.filter_by(book_status=0).all()
        # 如果条目少于或等于10条，直接返回所有条目
        if len(query_result) > 10:
            # 从所有条目中随机选择10条
            query_result = random.sample(Book.query.filter_by(book_status=0).all(), 10)
        pageTotal = len(query_result)
    elif 'id'  in request.get_json():
        query_result = Book.query.filter_by(id=request.get_json()['id']).all()
        pageTotal = len(query_result)
    else:
        # 初始化查询条件列表
        query_conditions = []
        # 根据json_data中的字段构建查询条件
        if request.get_json()['bookname'] != '':
            query_conditions.append(Book.name.contains(request.get_json()['bookname']))
        if request.get_json()['publisher'] != '':
            query_conditions.append(Book.publishing == request.get_json()['publisher'])
        if request.get_json()['author'] != '':
            query_conditions.append(Book.author == request.get_json()['author'])
        query_conditions.append(Book.book_status == 0)

        # 如果query_conditions为空，说明没有提供任何查询条件，可以决定返回一个空列表或执行其他操作
        if not query_conditions:
            query_result = []  # 或者可以抛出错误，或者返回所有书籍等
        else:
            # 使用and_连接所有查询条件，并执行查询
            query_result = Book.query.filter(and_(*query_conditions)).all()
        pageTotal = len(query_result)
    for i in query_result:
        book = dict(i)
        # 通过书籍反向关联查询出版社和作者名称
        book['publishing'] = i.backref_publisher.name
        book['author'] = i.backref_author.name
        book['book_type'] = i.backref_classification.type_name
        book['publish_time'] = int(dict(i)['publish_time'].timestamp())
        book['inbound_time'] = int(dict(i)['inbound_time'].timestamp())
        if i.outbound_time is not None:
            book['outbound_time'] = int(dict(i)['outbound_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.expire_time is not None:
            book['expire_time'] = int(dict(i)['expire_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.photo:
            photo_addr = 'http://' + settings.Config.SERVER_IP + ":" + str(settings.Config.SERVER_PORT) + i.photo
        else:
            photo_addr = ''

        book['photo'] = photo_addr
        query_list.append(book)
    response = {"status": True, "message": "查询成功", "infos": query_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/book/count', methods=['POST'])
@require_access_token
def book_count(current_user):
    count = len(Book.query.all())
    response = {"status": True, "message": "统计成功", "count": count}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/book/count_by_publishing', methods=['POST'])
@require_access_token
def book_count_by_college(current_user):
    # 查询所有出版社及对应的书籍数量
    publishing_with_book_counts = Publisher.query.outerjoin(Book).group_by(Publisher.id).with_entities(Publisher,
                                                                                                       func.count(
                                                                                                           Book.id).label(
                                                                                                           'book_count')
                                                                                                       ).all()
    # 查询所有图书类别及对应的书籍数量
    classification_with_book_counts=Classification.query.outerjoin(Book).group_by(Classification.id).with_entities(Classification,
                                                                                                       func.count(
                                                                                                           Book.id).label(
                                                                                                           'book_count')
                                                                                                       ).all()
    inbound_number = len(Book.query.filter_by(book_status=0).all())
    outbound_number = len(Book.query.filter_by(book_status=1).all())
    miss_number = len(Book.query.filter_by(book_status=2).all())
    expired_number = len(Book.query.filter(db.func.now() > (Book.outbound_time + timedelta(days=30))).all())
    response = {"status": True, "message": "查询成功",
                "infos": [{"name": publishing['name'], "number": book_count} for (publishing, book_count) in
                          publishing_with_book_counts],
                "classification_infos": [{"name": classification.type_name, "number": book_count} for (classification, book_count) in
                          classification_with_book_counts]}
    response.update({"statistics": {"inbound_number": inbound_number, "outbound_number": outbound_number,
                                    "miss_number": miss_number, "expired_number": expired_number}})
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/book/count_by_score', methods=['POST'])
@require_access_token
def book_count_by_score(current_user):
    query_result = Book.query.order_by(Book.score.desc()).limit(10).all()
    query_list=[]
    for i in query_result:
        book = dict(i)
        query_list.append({"name":book["name"],"score":book["score"]})
    response = {"status": True, "message": "查询成功", "infos": query_list}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/entry/update', methods=['POST'])
@require_access_token
def book_update(current_user):
    update_dict = {}
    if request.get_json()["author"]:
        update_dict.update({'author': request.get_json()["author"]})
    if request.get_json()["publishing"]:
        update_dict.update({'publishing': request.get_json()["publishing"]})
    if request.get_json()["book_type"] != '':
        update_dict.update({'book_type': request.get_json()["book_type"]})
    if request.get_json()["book_price"] != '':
        update_dict.update({'book_price': request.get_json()["book_price"]})
    if request.get_json()["publish_time"] != '':
        update_dict.update({'publish_time': request.get_json()["publish_time"]})
    if request.get_json()["photo"] != '':
        update_dict.update({'photo': request.get_json()["photo"]})
    if request.get_json()["description"] != '':
        update_dict.update({'description': request.get_json()["description"]})

    try:
        book = Book.query.filter_by(isbn_number=request.get_json()["isbn_number"])
        book.update(update_dict)
        # 提交更新到数据库（事务提交）
        db.session.commit()
        response = {"code": 0, "message": "更新成功!", "status": True}
        insert_audit_log(request.remote_addr, current_user, model_name, '更新图书信息: ' + book.first().name)
    except Exception as e:
        logger.exception(e)
        db.session.rollback()
        logger.error("update book info fail")
        response = {"code": -1, "message": "更新失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/borrow', methods=['POST'])
@require_access_token
def book_borrow(current_user):
    book = Book.query.filter_by(id=request.get_json()["id"])
    if book is None:
        response = {"code": -1, "message": "图书信息不存在!", "status": False}
    else:
        if book.first()['book_status'] != 0:
            response = {"code": -1, "message": "图书不能借阅!", "status": False}
        else:
            try:
                book.update(
                    {'book_status': 1, "outbound_time": datetime.now(), "borrowers": request.get_json()["username"],
                     "expire_time": datetime.now() + timedelta(days=30)})
                # 提交更新到数据库（事务提交）
                db.session.commit()
                response = {"code": 0, "message": "借阅成功!", "status": True}
                insert_audit_log(request.remote_addr, current_user, model_name, '借阅图书: ' + book.first().name)
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                logger.error("borrow book info fail")
                response = {"code": -1, "message": "借阅失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# 收藏图书
@book_bp.route('/collect', methods=['POST'])
@require_access_token
def book_collect(current_user):
    book = Book.query.filter_by(id=request.get_json()["id"])
    if book is None:
        response = {"code": -1, "message": "图书信息不存在!", "status": False}
    else:
        if User.query.filter_by(name=current_user).first().book_collect_list is None:
            User.query.filter_by(name=current_user).update({"book_collect_list": str(request.get_json()["id"])})
        else:
            if str(request.get_json()["id"]) in User.query.filter_by(name=current_user).first().book_collect_list:
                response = {"code": -1, "message": "你已经收藏过此图书啦!", "status": False}
                return jsonify(response)
            else:
                User.query.filter_by(name=current_user).update({"book_collect_list": User.query.filter_by(
                    name=current_user).first().book_collect_list + "," + str(request.get_json()["id"])})
        try:
            db.session.commit()
            insert_audit_log(request.remote_addr, current_user, model_name,
                             '收藏图书: ' + Book.query.get(request.get_json()["id"]).name)
            response = {"code": 1, "message": "收藏成功!", "status": True}
        except Exception as e:
            logger.exception(e)
            logger.error("update user book_collect_list fail")
            response = {"code": -1, "message": "收藏失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# 取消收藏图书
@book_bp.route('/collect/cancel', methods=['POST'])
@require_access_token
def book_collect_cancel(current_user):
    book = Book.query.filter_by(id=request.get_json()["id"])
    if book is None:
        response = {"code": -1, "message": "图书信息不存在!", "status": False}
    else:
        if str(request.get_json()["id"]) not in User.query.filter_by(name=current_user).first().book_collect_list:
            response = {"code": -1, "message": "尚未收藏过此图书!", "status": False}
            return jsonify(response)
        else:
            book_collect_list = User.query.filter_by(name=current_user).first().book_collect_list.split(",")
            book_collect_list = [item for item in book_collect_list if item != str(request.get_json()["id"])]
            new_book_collect_list = ','.join(i for i in book_collect_list)
            User.query.filter_by(name=current_user).update({"book_collect_list": new_book_collect_list})
        try:
            db.session.commit()
            insert_audit_log(request.remote_addr, current_user, model_name,
                             '取消收藏图书: ' + Book.query.get(request.get_json()["id"]).name)
            response = {"code": 1, "message": "取消收藏成功!", "status": True}
        except Exception as e:
            logger.exception(e)
            logger.error("update user book_collect_list fail")
            response = {"code": -1, "message": "取消收藏失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# 查看指定用户图书收藏列表
@book_bp.route('/collection/query', methods=['POST'])
@require_access_token
def book_collect_query(current_user):
    book_list = []
    query_result = User.query.filter_by(name=current_user).first().book_collect_list.strip(",")
    if query_result is None:
        response = {"status": True, "message": "查询成功", "infos": book_list, "pageTotal": 0}
    else:
        pageTotal = len(query_result.split(","))
        for i in query_result.split(","):
            book_ojb = Book.query.get(int(i))
            logger.debug(book_ojb)
            book = dict(book_ojb)
            # 通过书籍反向关联查询出版社和作者名称
            book['publishing'] = book_ojb.backref_publisher.name
            book['author'] = book_ojb.backref_author.name
            book['book_type'] = book_ojb.backref_classification.type_name
            book['publish_time'] = int(dict(book_ojb)['publish_time'].timestamp())
            book['inbound_time'] = int(dict(book_ojb)['inbound_time'].timestamp())
            if book_ojb.outbound_time is not None:
                book['outbound_time'] = int(dict(book_ojb)['outbound_time'].timestamp())
            else:
                book['outbound_time'] = ''
            if book_ojb.expire_time is not None:
                book['expire_time'] = int(dict(book_ojb)['expire_time'].timestamp())
            else:
                book['outbound_time'] = ''
            if book_ojb.photo:
                photo_addr = 'http://' + settings.Config.SERVER_IP + ":" + str(
                    settings.Config.SERVER_PORT) + book_ojb.photo
            else:
                photo_addr = ''

            book['photo'] = photo_addr
            book_list.append(book)
        response = {"status": True, "message": "查询成功", "infos": book_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/borrow/query', methods=['POST'])
@require_access_token
def book_borrow_query(current_user):
    query_conditions = []
    if request.get_json()['username'] == 'admin':
        query_conditions.append(Book.book_status == 1)
    else:
        query_conditions.append(Book.borrowers == (request.get_json()['username']))
        if 'bookname' in request.get_json() and request.get_json()['bookname'] != '':
            query_conditions.append(Book.name.contains(request.get_json()['bookname']))
        if 'publisher' in request.get_json() and request.get_json()['publisher']:
            query_conditions.append(Book.publishing == (request.get_json()['publisher']))
        if 'author' in request.get_json() and request.get_json()['author']:
            query_conditions.append(Book.author == (request.get_json()['author']))
    query_result = Book.query.filter(and_(*query_conditions)).all()
    query_list = []
    pageTotal = len(query_result)
    for i in query_result:
        book = dict(i)
        # 通过书籍反向关联查询出版社和作者名称
        book['publishing'] = i.backref_publisher.name
        book['author'] = i.backref_author.name
        book['publish_time'] = int(dict(i)['publish_time'].timestamp())
        book['inbound_time'] = int(dict(i)['inbound_time'].timestamp())
        if i.outbound_time is not None:
            book['outbound_time'] = int(dict(i)['outbound_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.expire_time is not None:
            book['expire_time'] = int(dict(i)['expire_time'].timestamp())
        else:
            book['outbound_time'] = ''
        if i.photo:
            photo_addr = 'http://' + settings.Config.SERVER_IP + ":" + str(settings.Config.SERVER_PORT) + i.photo
        else:
            photo_addr = ''

        book['photo'] = photo_addr
        query_list.append(book)
    response = {"status": True, "message": "查询成功", "infos": query_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# @book_bp.route('/borrow/back', methods=['POST'])
# @require_access_token
# def book_back(current_user):
#     book = Book.query.filter_by(id=request.get_json()['id'])
#     if book is not None:
#         if book.first()['borrowers'] != request.get_json()['username'] and current_user != 'admin':
#             response = {"code": -1, "message": "借阅人信息不匹配!", "status": False}
#         else:
#             try:
#                 book.update({"book_status": 0, "borrowers": "", "outbound_time": None})
#                 db.session.commit()
#                 response = {"code": 0, "message": "归还成功!", "status": True}
#                 # audit_logger.debug(
#                 #     "[{0}] [{1}] [{2}] [归还图书: {3}]".format(request.remote_addr, current_user, '图书管理',
#                 #                                                book.first().name))
#                 insert_audit_log(request.remote_addr, current_user, model_name, '归还图书: ' + book.first().name)
#             except Exception as e:
#                 logger.exception(e)
#                 db.session.rollback()
#                 logger.error("return book  fail")
#                 response = {"code": -1, "message": "归还失败!", "status": False}
#     else:
#         response = {"code": -1, "message": "书籍信息错误!", "status": False}
#     logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
#     return jsonify(response)
@book_bp.route('/borrow/back', methods=['POST'])
@require_access_token
def book_back(current_user):
    book = Book.query.filter_by(id=request.get_json()['id'])
    if book is not None:
        if book.first()['borrowers'] != request.get_json()['username'] and current_user != 'admin':
            response = {"code": -1, "message": "借阅人信息不匹配!", "status": False}
        else:
            try:
                if book.first()['score'] != 0:
                    new_score = round((book.first()['score'] + request.get_json()['score']) / 2, 2)
                else:
                    new_score = request.get_json()['score']
                book.update({"book_status": 0, "borrowers": "", "outbound_time": None, "score": new_score})
                db.session.commit()
                response = {"code": 0, "message": "归还成功!", "status": True}
                insert_audit_log(request.remote_addr, current_user, model_name, '归还图书: ' + book.first().name+" 并对它评分:"+str(request.get_json()['score'])+"分")
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                logger.error("return book  fail")
                response = {"code": -1, "message": "归还失败!", "status": False}
    else:
        response = {"code": -1, "message": "书籍信息错误!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/entry/delete', methods=['POST'])
@require_access_token
def book_delete(current_user):
    failed_item_ids = []
    if not isinstance(request.get_json()["id"], list):
        delete_ids = [request.get_json()["id"]]
    else:
        delete_ids = request.get_json()["id"]
    for student_id in delete_ids:
        query_book = Book.query.get(student_id)
        # 判断该条目是否存在
        if query_book is None:
            logger.error("delete {0} from table book fail".format(request.get_json()))
            failed_item_ids.append(student_id)
        else:
            try:
                db.session.delete(query_book)  # 将对象放在缓存中准备删除
                db.session.commit()  # 提交事务，删除
                logger.success("delete {0} from table book success".format(request.get_json()))
                # audit_logger.debug(
                #     "[{0}] [{1}] [{2}] [删除图书: {3}]".format(request.remote_addr, current_user, '图书管理',
                #                                                query_book.name))
                insert_audit_log(request.remote_addr, current_user, model_name, '删除图书: ' + query_book.name)
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                failed_item_ids.append(student_id)
                logger.error("delete {0}  from table book fail".format(request.get_json()))
    if len(failed_item_ids) == 0:
        response = {"status": "success", "code": 0, "message": '删除成功'}
    elif len(failed_item_ids) == len(request.get_json()["id"]):
        response = {"status": "fail", "code": -2, "message": '删除失败'}
    else:
        response = {"status": "success", "code": -1, "message": '部分条目删除失败'}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@book_bp.route('/upload', methods=['POST'])
@require_access_token
def file_upload(current_user):
    # logger.debug("接口请求数据:" + json.dumps(request.get_json()))
    # 'file'为前端表单中文件输入字段的名称，返回的的是一个FileStorage容器
    file = request.files['file']
    if file:
        # 上传的文件名
        filename = secure_filename(file.filename)
        # 将文件保存到服务器指定目录
        file_path = settings.Config.UPLOAD_FOLDER + filename
        try:
            file.save(file_path)
            # 计算图片md5值作为图片ID
            md5_obj = hashlib.md5()
            with open(file_path, 'rb') as file_obj:
                md5_obj.update(file_obj.read())
            img_id = md5_obj.hexdigest()
            new_file_name = img_id + "." + file.filename.split('.')[-1]
            # 对服务器存储的资源文件进行重命名并返回该图片的路径
            if not os.path.exists(settings.Config.UPLOAD_FOLDER + new_file_name):
                os.rename(file_path, settings.Config.UPLOAD_FOLDER + new_file_name)
                response = {'code': 0, 'message': '上传成功', 'path': url_for('static', filename=f'{new_file_name}'),
                            'status': True}
                insert_audit_log(request.remote_addr, current_user, model_name, '上传了文件: ' + filename)
            else:
                response = {'code': -1, 'message': '文件已存在', 'status': False}
        except Exception as e:
            logger.exception(e)
            response = {'code': -1, 'message': '上传失败', 'status': False}
        logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
        return jsonify(response)


@book_bp.route('/batch_upload', methods=['POST'])
@require_access_token
def excel_upload(current_user):
    # 确保请求中包含文件
    if 'file' not in request.files:
        return jsonify({'code': -1, 'message': '文件不存在', 'status': False})
    file = request.files['file']
    # 检查文件是否为空
    if file.filename == '':
        return jsonify({'code': -1, 'message': '文件为空', 'status': False})
    # 确保是Excel文件
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({'code': -1, 'message': '只能上传xls,xlsx格式文件', 'status': False})
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        # 将DataFrame转换为字典列表，准备插入数据库
        books_data = df.to_dict(orient='records')
        # 遍历数据，创建Book对象并添加到session
        for book_info in books_data:
            if Book.query.filter_by(isbn_number=str(book_info['ISBN条形码'])).first() is not None:
                print("已存在该条形码：" + str(book_info['ISBN条形码']))
                continue
            else:
                book_max_id_query = db.session.query(func.max(Book.id)).scalar()
                if book_max_id_query is None:
                    max_id = 10000
                else:
                    max_id = book_max_id_query

                if Publisher.query.filter_by(name=book_info['出版社']).first() is not None:
                    publish_id = Publisher.query.filter_by(name=book_info['出版社']).first().id
                else:
                    # 出版社不存在创建出版社
                    publish_max_id_query = db.session.query(func.max(Publisher.id)).scalar()
                    publish_id = publish_max_id_query + 1
                    col = Publisher(publish_id=publish_id, name=book_info['出版社'])
                    db.session.add(col)  # 添加一条
                    db.session.commit()
                    insert_audit_log(request.remote_addr, current_user, model_name,
                                     '批量上传图书时自动创建出版社: ' + book_info['出版社'])

                if Author.query.filter_by(name=book_info['作者']).first() is not None:
                    author_id = Author.query.filter_by(name=book_info['作者']).first().id
                else:
                    # 作者不存在创建
                    author_max_id_query = db.session.query(func.max(Author.id)).scalar()
                    author_id = author_max_id_query + 1
                    col = Author(author_id=author_id, name=book_info['作者'])
                    db.session.add(col)  # 添加一条
                    # 提交事务
                    db.session.commit()
                    insert_audit_log(request.remote_addr, current_user, model_name,
                                     '批量上传图书时自动创建作者: ' + book_info['作者'])

                if Classification.query.filter_by(type_name=book_info['所属类别']).first() is not None:
                    classification_id = Classification.query.filter_by(type_name=book_info['所属类别']).first().id
                else:
                    # 图书类别不存在创建
                    classification_max_id_query = db.session.query(func.max(Publisher.id)).scalar()
                    classification_id = classification_max_id_query + 1
                    col = Classification(book_class_id=classification_id, type_name=book_info['所属类别'])
                    db.session.add(col)  # 添加一条
                    # 提交事务
                    db.session.commit()
                    insert_audit_log(request.remote_addr, current_user, model_name,
                                     '批量上传图书时自动创建图书类别: ' + book_info['所属类别'])

                new_book = Book(
                    book_id=max_id + 1,
                    name=book_info['书名'],
                    isbn_number=str(book_info['ISBN条形码']),
                    publishing=publish_id,
                    author=author_id,
                    book_type=classification_id,
                    book_price=book_info.get('价格', None),  # 处理可能的空值
                    publish_time=book_info.get('出版时间', None),  # 转换日期格式可能需要额外处理
                    book_status=0,
                    inbound_time=datetime.now(),

                )
                db.session.add(new_book)
                if len(book_info['简介']) != 0:
                    new_book.description = book_info['简介']
                if len(book_info['封面图片']) != 0:
                    new_book.photo = book_info['封面图片']
        # 提交事务
        db.session.commit()
        response = {"code": 0, "message": "批量录入成功!", "status": True}
        insert_audit_log(request.remote_addr, current_user, model_name, '批量上传了图书文件: ' + file.filename)

    except Exception as e:
        db.session.rollback()  # 发生错误时回滚事务
        logger.exception(e)
        logger.error("batch insert book  info from {0} fail".format(file.filename))
        response = {"code": -1, "message": "批量录入失败!", "status": False}

    return jsonify(response)


@book_bp.route('/<path:filename>', methods=['GET'])
def serve_image(filename):
    if filename in settings.Config.ALLOWED_EXTENSIONS:
        image_absolute_url = url_for('static', filename=f'{filename}')
        return image_absolute_url
    else:
        # return jsonify({"message":"当前用户未登录，请重新登录"})
        return redirect(settings.DevelopmentConfig.VUE_ADDR)
