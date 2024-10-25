#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
@Time    : 2023年03月18日18:57分
@Author  : Anonymous
@Description: 
'''
from datetime import datetime

from exts import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    role_id = db.Column(db.Integer)
    register_time = db.Column(db.DateTime, default=datetime.now())
    last_login_time = db.Column(db.DateTime, default=datetime.now())
    ip = db.Column(db.String(15))
    description = db.Column(db.String(256))
    book_collect_list = db.Column(db.String(1024))

    def __init__(self, u_id, name, password, email, role_id=0):
        self.id = u_id
        self.name = name
        self.password = password
        self.email = email
        self.role_id = int(role_id)

    def __str__(self):
        return self.name

    def keys(self):
        return ('id', 'name', 'email', 'role_id', 'register_time', 'last_login_time', 'ip', 'description')

    def __getitem__(self, item):
        return getattr(self, item)
