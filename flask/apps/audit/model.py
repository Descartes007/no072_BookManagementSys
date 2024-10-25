#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/14 9:05
# Description: xxx
from datetime import datetime

from exts import db


class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    op_time = db.Column(db.DateTime, default=datetime.now())
    op_ip = db.Column(db.String(15), nullable=False)
    op_user = db.Column(db.String(32), nullable=False, default='')
    op_module = db.Column(db.String(32), nullable=False, default='')
    op_event = db.Column(db.String(64), nullable=False, default='')

    def __init__(self, op_ip, op_user, op_module, op_event):
        self.op_time = datetime.now()
        self.op_ip = op_ip
        self.op_user = op_user
        self.op_module = op_module
        self.op_event = op_event

    def __str__(self):
        return self.id

    def to_dict(self):
        return {
            'id': self.id,
            'op_time': self.op_time,
            'op_ip': self.op_ip,
            'op_user': self.op_user,
            'op_module': self.op_module,
            'op_event': self.op_event,

        }
    # def keys(self):
    #     return ('id', 'name', 'permission_ids')
    #
    # def __getitem__(self, item):
    #     return getattr(self, item)
