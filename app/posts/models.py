from flask.ext.login import UserMixin
from app import database, store
from app.mixins import CRUDMixin

from storm.locals import *
import datetime

class Post(CRUDMixin, Storm):
    __storm_table__ = "posts"    
    title = Unicode(default=u'')
    body = Unicode(default=u'')
    user_id = Int(default=0)
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
   
    def __repr__(self): # pragma: no cover
        return '<Post %r>' % (self.title)

    @staticmethod
    def create_table():
      store.execute("CREATE TABLE posts "
                    "(id SERIAL PRIMARY KEY,\
                      title VARCHAR(128) NOT NULL,\
                      body TEXT,\
                      user_id INTEGER,\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX posts_title_idx ON posts USING btree (title);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='posts');").get_one()
      return result[0]

    @staticmethod
    def get_user_posts(user_id = 1, limit = 10, page = 1):
      result = store.find(Post, Post.user_id == user_id)
      return result.order_by(Desc(Post.id)).config(limit=limit, offset=(page-1)*limit)
