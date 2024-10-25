#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/10 10:41
# Description: 出版社模型
from exts import db


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    # 一个出版社可以有很多图书,backref='backref_publish'用于通过图书实例.backref_publish就可以找到出版社实例,backref参数来创建反向引用
    books = db.relationship('Book', backref='backref_publisher', lazy='dynamic')
    def __init__(self, publish_id, name):
        self.id = publish_id
        self.name = name

    # 这2个方法必须加上，否则query.all()查询表中的数据返回给前端的时候会报错TypeError: Object of type Element is not JSON serializable
    # [dict(i) for i in Element.query.all()]可以将查询到的数据转为列表
    def keys(self):
        return ('id', 'name')

    def __getitem__(self, item):
        return getattr(self, item)