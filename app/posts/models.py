from flask.ext.login import current_user
from app import store
from app.mixins import CRUDMixin
from storm.locals import *
from app.users.models import User
import datetime


class Post(CRUDMixin):
    __storm_table__ = "posts"
    title = Unicode(default=u'')
    body = Unicode(default=u'')
    extra_body = Unicode(default=u'')
    is_anonymous = Int(default=0)
    slug = Unicode(default=u'')
    user_id = Int()
    category_id = Int(default=1)
    image_url = Unicode(default=u'')
    created_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    user = Reference(user_id, User.id)
    category = Reference(category_id, 'Category.id')

    def __repr__(self): # pragma: no cover
      return '<Post %r>' % (self.title)

    def is_mine(self):
      return current_user.is_authenticated and self.user.id == current_user.id

    def can_edit(self):
      return current_user.is_authenticated and (self.user.id == current_user.id or current_user.is_admin())

    @classmethod
    def get_by_slug(cls, slug):
      return store.find(cls, cls.slug == slug).one()

    @classmethod
    def check_if_slug_is_taken(cls, id, slug):
      if id:
          return store.find(cls, cls.id != id, cls.slug == slug).count()
      else:
          return store.find(cls, cls.slug == slug).count()

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
