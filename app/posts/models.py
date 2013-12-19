from flask.ext.login import UserMixin
from app import app, database, store
from app.mixins import CRUDMixin
from storm.locals import *
from app.users.models import User
import datetime

class Post(CRUDMixin):
    __storm_table__ = "posts"    
    title = Unicode(default=u'')
    body = Unicode(default=u'')
    user_id = Int()
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    user = Reference(user_id, User.id)

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

# class UserPosts(object):
#     __storm_table__ = "userposts"
#     __storm_primary__ = "user_id", "post_id"
#     user_id = Int()
#     post_id = Int()

#     @staticmethod
#     def create_table():
#       store.execute("CREATE TABLE userposts (user_id INTEGER, post_id INTEGER, PRIMARY KEY (user_id, post_id))")
#       store.commit()
#       return True

#     @staticmethod
#     def exist_table():
#       result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='userposts');").get_one()
#       return result[0]
