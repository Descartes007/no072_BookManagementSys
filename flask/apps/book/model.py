#!/usr/bin/env python3
# ! -*- coding=utf-8 -*-
'''
**************************************************************
** @Create：2024/2/26 10:50
** @Author：anonymous
** @Description：图书模型
**************************************************************
'''

from datetime import datetime
from exts import db


# 图书信息
class Book(db.Model):
    # 可以自定义表的名称，不用模型的名称
    __tablename__ = 'book'
    # 图书编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, default=10000)
    # 书名
    name = db.Column(db.String(64), unique=True, nullable=False)
    # 条形码
    isbn_number = db.Column(db.String(17), unique=True, nullable=False)
    # 出版社
    publishing = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    # 作者
    author = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    # 图书类别
    book_type = db.Column(db.Integer, db.ForeignKey('classification.id'), nullable=False)
    # 图书价格
    book_price = db.Column(db.Float, nullable=False)
    # 当前状态(0-入库,1-已借出,2-丢失)
    book_status = db.Column(db.Integer, nullable=False, default=0)
    # 出版时间
    publish_time = db.Column(db.DateTime, default=datetime.now())
    # 入库时间
    inbound_time = db.Column(db.DateTime, default=datetime.now())
    # 出库时间
    outbound_time = db.Column(db.DateTime)
    # 到期时间
    expire_time = db.Column(db.DateTime)
    # 借阅人、读者
    borrowers = db.Column(db.String(32))
    # 图书照片
    photo = db.Column(db.String(48))
	# 图书评分
    score = db.Column(db.Float, default=0)
    # 简介
    description = db.Column(db.String(1024))

    def __init__(self, book_id, name, isbn_number, publishing, author, book_type, publish_time, book_price, book_status,
                 inbound_time):
        self.id = book_id
        self.name = name
        self.isbn_number = isbn_number
        self.publishing = publishing
        self.author = author
        self.book_type = book_type
        self.publish_time = publish_time
        self.book_price = book_price
        self.book_status = book_status
        self.inbound_time = inbound_time

    def keys(self):
        return (
            'id', 'name', 'isbn_number', 'publishing', 'author', 'publish_time', 'book_price', 'book_status',
            'inbound_time', 'outbound_time', 'borrowers', 'photo', 'description', 'expire_time', 'book_type','score')

    def __getitem__(self, item):
        return getattr(self, item)
