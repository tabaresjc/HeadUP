from flask.ext.login import UserMixin
from app import app, database, store
from app.mixins import CRUDMixin
from storm.locals import *
import datetime


class Comment(CRUDMixin):
	__storm_table__ = "comments"
    user_id = Int()
    post_id = Int()
    body = Unicode(default=u'')
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))   
    
    @staticmethod
    def create_table():
      store.execute("CREATE TABLE comments "
                    "(id SERIAL PRIMARY KEY,\
                      user_id INTEGER,\
                      post_id INTEGER,\
                      body VARCHAR(512),\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX users_email_idx ON users USING btree (email);", noresult=True)
      store.execute("CREATE INDEX users_nickname_idx ON users USING btree (nickname);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():      
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='comments');").get_one()
      return result[0]