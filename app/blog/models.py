from flask.ext.login import UserMixin
from flask.ext.login import current_user
from app import app, database, store
from app.mixins import CRUDMixin
from storm.locals import *
from app.users.models import User
from app.posts.models import Post
import datetime

class Search(object):
    @staticmethod
    def search_post(keyword, limit=10, page=1):
    	count = 0
    	records = store.find(Post, Or(
    		Post.title.like(u'%'+keyword+u'%', case_sensitive=False),
    		Post.body.like(u'%'+keyword+u'%', case_sensitive=False)
    		))
    	count = records.count()
    	records = records.order_by(Desc(Post.id)).config(limit=limit, offset=(page-1)*limit)
    	return records, count
