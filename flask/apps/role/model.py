#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/1 23:05
# Description: xxx


from exts import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(16), unique=True)
    permission_ids = db.Column(db.String(256), nullable=False)

    def __init__(self, role_id, name, permission_ids=''):
        self.id = role_id
        self.name = name
        self.permission_ids = permission_ids

    def __str__(self):
        return self.name

    def keys(self):
        return ('id','name', 'permission_ids')

    def __getitem__(self, item):
        return getattr(self, item)
