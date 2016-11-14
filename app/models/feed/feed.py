# -*- coding: utf8 -*-

from app import db
from math import log
import datetime


class Feed:

    epoch = datetime.datetime(1970, 1, 1)

    @classmethod
    def epoch_seconds(cls, date):
        td = date - cls.epoch
        return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

    @classmethod
    def score(cls, ups, downs):
        return ups - downs

    @classmethod
    def hot(cls, ups, downs, date):
        s = cls.score(ups, downs)
        order = log(max(abs(s), 1), 10)
        sign = 1 if s > 0 else -1 if s < 0 else 0
        seconds = cls.epoch_seconds(date) - 1134028003
        return round(sign * order + seconds / 45000, 7)

    @classmethod
    def posts(cls, page=1, limit=10):
        from app.models import Post
        query = Post.query
        count = query.count()
        records = []
        if count:
            order = db.text('created_at DESC')
            offset = (page - 1) * limit
            records = query.order_by(order).limit(limit).offset(offset)
        return records, count

    @classmethod
    def ranking(cls, page=1, limit=20):
        from app.models import Post
        query = Post.query
        count = query.count()
        records = []
        if count:
            order = db.text('created_at DESC')
            offset = (page - 1) * limit
            records = query.order_by(order).limit(limit).offset(offset)
        return records, count
