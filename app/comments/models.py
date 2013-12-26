from flask.ext.login import UserMixin
from app import app, database, store
from app.mixins import CRUDMixin
from storm.locals import *
from app.users.models import User
from app.posts.models import Post
import datetime


class Comment(CRUDMixin):
    __storm_table__ = "comments"
    body = Unicode(default=u'')
    user_id = Int(default=0)
    post_id = Int(default=0)
    comment_id = Int(default=0)
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))   
    user = Reference(user_id, User.id)
    post = Reference(post_id, Post.id)
    reply = Reference(comment_id, id)

    def __repr__(self): # pragma: no cover
      return '<Comment %s>' % (self.id)

    @staticmethod
    def create_table():
      store.execute("CREATE TABLE comments "
                    "(id SERIAL PRIMARY KEY,\
                      body VARCHAR(16384),\
                      user_id INTEGER,\
                      post_id INTEGER,\
                      comment_id INTEGER,\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX comments_users_idx ON comments USING btree (user_id);", noresult=True)
      store.execute("CREATE INDEX comments_posts_idx ON comments USING btree (post_id);", noresult=True)
      store.execute("CREATE INDEX comments_comment_idx ON comments USING btree (comment_id);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():      
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='comments');").get_one()
      return result[0]