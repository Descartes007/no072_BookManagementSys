#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/13 14:11
# Description: 自定义请求头校验规则不使用jwt-extended自带的bearer规则
from flask import request, jsonify, current_app
from flask_jwt_extended import decode_token, get_jwt_identity
from functools import wraps


def require_access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('X-Access-Token', None)
        if not access_token:
            return jsonify({'status': True, 'message': '非法请求，请先登录!', 'flag': 'token'}), 401
        try:
            # 对token进行解码
            claims = decode_token(access_token)
            # 假设你的 token 中包含 'identity' 字段作为用户标识
            current_user = claims['sub']
            redis_store = current_app.extensions['redis']
            # 将请求头的token值和redis存储的token值进行校验不一致就认为过期
            if redis_store.get(current_user).decode() != access_token:
                return jsonify({'status': True, 'message': 'token已过期!', 'flag': 'token'}), 401
        except Exception as e:
            return jsonify({'status': True, 'message': 'token已过期!', 'flag': 'token'}), 401
        return func(current_user, *args, **kwargs)

    return wrapper


def jwt_refresh_token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        refresh_token = request.headers.get('Refresh-Token', None)
        if not refresh_token:
            return jsonify({'status': True, 'message': 'Refresh Token非法，请先登录!', 'flag': 'refresh token'}), 401
        try:
            # 对refresh_token进行解码
            claims = decode_token(refresh_token)
            # 假设你的 refresh_token 中包含 'identity' 字段作为用户标识
            current_user = claims['sub']
            redis_store = current_app.extensions['redis']
            # 将请求头的refresh token值和redis存储的refresh token值进行校验不一致就认为过期
            if redis_store.get(current_user + '-refresh_token').decode() != refresh_token:
                return jsonify({'status': True, 'message': 'Refresh Token已过期!', 'flag': 'refresh token'}), 401
        except Exception as e:
            return jsonify({'status': True, 'message': 'Refresh Token已过期!', 'flag': 'refresh token'}), 401
        return func(current_user, *args, **kwargs)

    return wrapper
