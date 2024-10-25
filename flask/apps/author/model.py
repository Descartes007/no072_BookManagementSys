#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
# Author: anonymous
# Create_Date: 2024/3/10 10:45
# Description: 图书作者模型
from exts import db


# 图书作者模型
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    books = db.relationship('Book', backref='backref_author', lazy='dynamic')
    # //book = db.Column(db.Integer, db.ForeignKey('book.id'))

    def __init__(self, author_id, name):
        self.id = author_id
        self.name = name


    def keys(self):
        return ('id', 'name')

    def __getitem__(self, item):
        return getattr(self, item)
