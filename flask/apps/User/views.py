#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
@Time    : 2023年03月18日18:58分
@Author  : Anonymous
@Description: 
'''

import json
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask import Blueprint, request, jsonify, url_for, make_response, session, g, redirect, current_app
from sqlalchemy import or_, func
import settings
from apps.User.model import User
from apps.role.model import Role
from exts import db
from exts.auth import require_access_token, jwt_refresh_token_required
from exts.common import generate_random_str, insert_audit_log
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger
from exts.sendmail import send_mail

user_bp = Blueprint('user', __name__)
model_name = '登录'


# 蓝图中的 endpoint 是相对于蓝图本身的，完整的 endpoint 名称包括蓝图的名称和视图函数的 endpoint。
@user_bp.route('/login', methods=['POST'], endpoint='user_login')
def login():
    # logger.debug("接口请求地址:" + request.url)
    # logger.debug("接口请求数据:" + json.dumps(request.get_json()))
    # 向数据库查询该用户信息
    user = User.query.filter_by(name=request.get_json()['username']).first()
    if user is not None:
        query_password = User.query.filter_by(name=request.get_json()['username']).first().password
        if query_password == request.get_json()['password']:
            # Flask-Login 需要 session ID 来维护登录状态，而不是自定义的 'key'。应该使用 Flask 的 session 对象来设置 session ID，而不是直接设置 cookie。
            # response.set_cookie('key','123456',max_age=3600,samesite='None', secure=True)
            # 将用户登录状态保存到会话中
            # login_user(user)
            # 创建token令牌并使用redis保存该用户的token
            token = create_access_token(identity=user.name)
            refresh_token = create_refresh_token(identity=user.name)
            redis_store = current_app.extensions['redis']
            try:
                redis_store.set(user.name, token)
                redis_store.set(user.name + "-refresh_token", refresh_token)
            except Exception as e:
                return make_response({"code": -1, "message": "redis连接异常！"})
            # 将用户 ID 保存到 session 中
            # session['user_id'] = user.id
            next_url = request.args.get('next')
            if next_url is not None:
                return make_response({"code": -1, "message": "请登录"})
            insert_audit_log(request.remote_addr, request.get_json()['username'], model_name, '账号登录')
            user.last_login_time = datetime.now()
            user.ip = request.remote_addr
            db.session.add(user)
            db.session.commit()
            response = make_response(
                {'status': True, 'message': '登录成功', 'token': token, 'refresh_token': refresh_token})
        else:
            response = make_response({'status': False, 'message': '登录失败，请检查用户名或密码是否正确'})

    else:
        response = make_response({'status': False, 'message': '登录失败，请检查用户名或密码是否正确'})
    # logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return response


@user_bp.route('/logout', methods=['POST'])
@require_access_token
def logout(current_user):
    # logout_user()
    # 把该用户的token加入黑名单标记为失效状态
    # get_jti_from_token(c)
    redis_store = current_app.extensions['redis']
    redis_store.get(current_user)
    redis_store.delete(current_user)
    logger.info("{0} username:{1} logout success".format(model_name, request.get_json()['username']))
    insert_audit_log(request.remote_addr, request.get_json()['username'], model_name, '退出登录')
    return {'status': True, 'message': '退出登录成功'}


# token过期需要重新生成token返回
@user_bp.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh(current_user):
    new_token = create_access_token(identity=current_user)
    redis_store = current_app.extensions['redis']
    redis_store.set(current_user, new_token)
    insert_audit_log(request.remote_addr, current_user, model_name, '更新了token')
    return jsonify({'status': True, 'message': '更新token成功', 'token': new_token})


@user_bp.route('/user/add', methods=['POST'])
@require_access_token
def user_add(current_user):
    # 此处向数据库查询有无冲突并添加用户返回给前端添加结果
    users = User.query.filter_by(name=request.get_json()["name"]).first()
    if users is None:
        max_id_query = db.session.query(func.max(User.id)).scalar()
        if max_id_query is None:
            max_id = 0
        else:
            max_id = max_id_query
        try:
            col = User(u_id=max_id + 1, name=request.get_json()["name"], password=request.get_json()["password"],
                       email=request.get_json()["email"], role_id=request.get_json()["role_id"])
            col.register_time = datetime.now()
            col.description = request.get_json()["description"]
            db.session.add(col)  # 添加一条
            # 提交事务
            db.session.commit()
            response = {"code": 0, "id": max_id + 1, "message": "创建成功!", "status": True}
            insert_audit_log(request.remote_addr, current_user, '用户管理', '新增用户' + request.get_json()['username'])
        except Exception as e:
            logger.exception(e)
            logger.error("commit user info fail")
            response = {"code": -1, "message": "创建失败!", "status": False}
    else:
        logger.error("add user info fail, info is exist")
        response = {"code": -1, "message": "条目已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route("/user/query", methods=['POST'])
@require_access_token
def user_query(current_user):
    user_list = []
    pageTotal = len(User.query.all())
    if len(request.get_json()) == 0:
        query_result = User.query.all()
    else:
        if "query_string" in request.get_json():
            query_string = request.get_json()['query_string']
            # 指定分页信息查询数据
            if query_string == '':
                page = int(request.get_json()['page'])
                size = int(request.get_json()['size'])
                offset = (page - 1) * size
                query_result = User.query.offset(offset).limit(size).all()
            # 指定关键字查询
            else:
                query_result = User.query.filter((User.name.contains(query_string))).all()
                pageTotal = len(query_result)
        else:
            # 指定用户名查询
            query_result = User.query.filter_by(name=request.get_json()['name']).all()
    for i in query_result:
        user_dict = dict(i)
        register_time = int(dict(i)['register_time'].timestamp())
        last_login_time = int(dict(i)['last_login_time'].timestamp())
        user_dict.update({'register_time': register_time, 'last_login_time': last_login_time})
        user_list.append(user_dict)
    response = {"status": True, "message": "查询成功", "infos": user_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route('/user/permission/query', methods=['POST'])
def user_permission_query():
    user_role_permission_list = []
    for i in User.query.all():
        data = {'name': i.name, 'permissions': Role.query.filter_by(id=i.role_id).first().permission_ids}
        user_role_permission_list.append(data)
    response = {'status': True, 'infos': user_role_permission_list}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# 用户中心更改密码和描述
@user_bp.route('/user_center/update', methods=['POST'])
@require_access_token
def user_center_update(current_user):
    # 查询用户是否存在
    logger.debug("接口请求数据:" + json.dumps(request.get_json()))
    user = User.query.filter_by(name=request.get_json()["name"]).first()
    if user is None:
        response = {"code": -1, "message": "用户不存在!", "success": False}
    else:
        # 判断提交的旧密码是否正确
        query_oldpwd = getattr(User.query.filter_by(name=request.get_json()["name"]).first(), 'password')
        logger.debug("数据库中查询结果:" + query_oldpwd)
        if query_oldpwd != request.get_json()['oldpwd']:
            response = {"code": -1, "message": "旧密码错误!", "success": False}
        else:
            try:
                User.query.filter_by(name=request.get_json()["name"]).update(
                    {'password': request.get_json()["newpwd"], 'description': request.get_json()["description"]})
                # 提交更新到数据库（事务提交）
                db.session.commit()
                response = {"code": 0, "message": "用户信息更新成功!", "status": True}
                insert_audit_log(request.remote_addr, current_user, '用户管理',
                                 '更新用户' + request.get_json()['name'] + '信息')
            except Exception as e:
                logger.exception(e)
                logger.error("update user info fail")
                response = {"code": -1, "message": "用户信息更新失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


# 管理员修改任意用户信息
@user_bp.route('/user/update', methods=['POST'])
@require_access_token
def user_update(current_user):
    # 查询用户是否存在
    logger.debug("接口请求数据:" + json.dumps(request.get_json()))
    user = User.query.filter_by(name=request.get_json()["name"]).first()
    if user is None:
        response = {"code": -1, "message": "用户不存在!", "success": False}
    else:
        try:
            User.query.filter_by(name=request.get_json()["name"]).update(
                {'password': request.get_json()["password"], 'email': request.get_json()["email"],
                 'role_id': request.get_json()["role_id"], 'description': request.get_json()["description"]})
            # 提交更新到数据库（事务提交）
            db.session.commit()
            response = {"code": 0, "message": "用户信息更新成功!", "status": True}
            insert_audit_log(request.remote_addr, current_user, '用户管理',
                             '更新' + request.get_json()['name'] + '用户信息')
        except Exception as e:
            logger.exception(e)
            db.session.rollback()
            logger.error("delete {0}  from table book fail".format(request.get_json()))
            response = {"code": -1, "message": "用户信息更新失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route('/user/count', methods=['POST'])
@require_access_token
def user_count(current_user):
    # 此处向数据库查询所有用户数量
    user = User.query.all()
    response = {"code": 0, "count": len(user), "status": True}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route('/user/delete', methods=['POST'])
@require_access_token
def user_delete(current_user):
    logger.debug("接口请求地址:" + request.url)
    logger.debug("接口请求数据:" + json.dumps(request.get_json()))
    failed_item_ids = []
    if not isinstance(request.get_json()["id"], list):
        delete_ids = [request.get_json()["id"]]
    else:
        delete_ids = request.get_json()["id"]
    for user_id in delete_ids:
        query_result = User.query.get(user_id)
        # 判断该条目是否存在
        if query_result is None:
            logger.error("delete {0} from table user fail".format(request.get_json()))
            failed_item_ids.append(user_id)
        else:
            try:
                db.session.delete(query_result)  # 将对象放在缓存中准备删除
                db.session.commit()  # 提交事务，删除
                logger.success("delete {0} from table user success".format(request.get_json()))
                insert_audit_log(request.remote_addr, current_user, '用户管理',
                                 '删除' + query_result.name + '用户信息')
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                failed_item_ids.append(user_id)
                logger.error("delete {0}  from table user fail".format(request.get_json()))
    if len(failed_item_ids) == 0:
        response = {"status": "success", "code": 0, "message": '删除成功'}
    elif len(failed_item_ids) == len(request.get_json()["id"]):
        response = {"status": "fail", "code": -2, "message": '删除失败'}
    else:
        response = {"status": "success", "code": -1, "message": '部分条目删除失败'}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route('/register', methods=['POST'])
def user_register():
    # 此处向数据库查询有无冲突并添加用户返回给前端添加结果
    users = User.query.filter_by(name=request.get_json()["username"]).first()
    if users is None:
        max_id_query = db.session.query(func.max(User.id)).scalar()
        if max_id_query is None:
            max_id = 0
        else:
            max_id = max_id_query
        try:
            col = User(u_id=max_id + 1, name=request.get_json()["username"], password=request.get_json()["password"],
                       email=request.get_json()["email"], role_id=2)
            col.register_time = datetime.now()
            db.session.add(col)  # 添加一条
            # 提交事务
            db.session.commit()
            response = {"code": 0, "id": max_id + 1, "message": "注册成功!", "status": True}
            insert_audit_log(request.remote_addr, request.get_json()["username"], '用户管理',
                             '用户: ' + request.get_json()["username"] + '注册')
        except Exception as e:
            logger.exception(e)
            logger.error("commit user info fail")
            response = {"code": -1, "message": "注册失败!", "status": False}
    else:
        logger.error("add user info fail, info is exist")
        response = {"code": -1, "message": "用户名或邮箱已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)


@user_bp.route('/reset_password', methods=['POST'])
def reset_user_password():
    # 此处向数据库查询该用户是否存在
    user = User.query.filter_by(name=request.get_json()["username"]).first()
    if user is None:
        logger.info("reset user password fail, user is error")
        response = {"code": -1, "message": "用户信息不正确!", "status": False}

    else:
        if request.get_json()["email"] != user.email:
            logger.info("reset user password fail, email is error")
            response = {"code": -1, "message": "用户信息不正确!", "status": False}
        else:
            # 重置密码
            new_random_password = generate_random_str(8)
            if send_mail(settings.Config.EMAIL_USERNAME, request.get_json()["email"], '用户密码找回',
                         '重置后的密码是{0}，请尽快登录后修改密码'.format(new_random_password)):
                # 提交更改到数据库
                try:
                    user.password = new_random_password
                    db.session.commit()
                except Exception as e:
                    logger.error("commit user new password to database fail")
                else:
                    logger.success("reset user password success".format(request.get_json()["username"]))
                    insert_audit_log(request.remote_addr, request.get_json()["username"], '用户管理', '重置密码')
                    response = {"code": 0, "message": "重置密码成功，请注意查收邮箱!", "status": True}
            else:
                response = {"code": -1, "message": "发送邮件失败!", "status": False}

    logger.debug("接口请求返回:" + json.dumps(response, ensure_ascii=False))
    return jsonify(response)
