from flask.ext.login import UserMixin, current_user
from flask.ext.babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash
from app import store
from app.mixins import CRUDMixin
from storm.locals import *
from hashlib import md5
import datetime
import re

ROLE_WRITER = 2
ROLE_ADMIN = 1


class User(UserMixin, CRUDMixin):
    __storm_table__ = "users"
    email = Unicode(default=u'')
    name = Unicode(default=u'')
    nickname = Unicode(default=u'')
    password = Unicode(default=u'')
    role = Int(default=ROLE_WRITER)
    address = Unicode(default=u'')
    phone = Unicode(default=u'')
    last_seen = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    last_login = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    timezone = Unicode(default=u'Asia/Tokyo')
    lang = Unicode(default=u'en')
    created_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    
    def set_password(self, password):
      self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
      return check_password_hash(self.password, password)

    def is_admin(self):
      return self.role == int(ROLE_ADMIN)

    def role_desc(self):
        if self.role == int(ROLE_ADMIN):
            return gettext('Admin')
        else:
            return gettext('Writer')

    def is_current(self):
      return self.id == current_user.id

    def avatar(self, size):
      return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self): # pragma: no cover
        return '<User %s %r>' % (self.id, self.name)

    def get_user_posts(self, limit=10, page=1):
      return self.posts.find().config(offset=(page - 1) * limit, limit=limit)

    def get_user_comments(self, limit=10, page=1):
      return self.comments.find().config(offset=(page - 1) * limit, limit=limit)

    @staticmethod
    def find_by_email(email):
      return store.find(User, User.email == email).one()

    @staticmethod
    def make_valid_name(name):
        return re.sub('[!#\[\]\(\)\.]', '', name)

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[!#\[\]\(\)\.]', '', nickname)

    @staticmethod
    def is_email_taken(email):
        if store.find(User, User.email == email).count() > 0:
          return True
        else:
          return False

    @staticmethod
    def is_nickname_taken(nickname):
        if store.find(User, User.nickname == nickname).count() > 0:
          return True
        else:
          return False
   
    @staticmethod
    def create_table():
      store.execute("CREATE TABLE users "
                    "(id SERIAL PRIMARY KEY,\
                      email VARCHAR(255) UNIQUE NOT NULL,\
                      name VARCHAR(64) UNIQUE NOT NULL,\
                      nickname VARCHAR(64) UNIQUE NOT NULL,\
                      password VARCHAR(255),\
                      role SMALLINT,\
                      address VARCHAR(255),\
                      phone VARCHAR(64),\
                      last_seen TIMESTAMP,\
                      last_login TIMESTAMP,\
                      timezone VARCHAR(20) DEFAULT 'Asia/Tokyo'::character varying,\
                      lang VARCHAR(20) DEFAULT 'en'::character varying,\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX users_email_idx ON users USING hash (email);", noresult=True)
      store.execute("CREATE INDEX users_nickname_idx ON users USING hash (nickname);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='users');").get_one()
      return result[0]
