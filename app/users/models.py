from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import database, store
from app.mixins import CRUDMixin
from storm.locals import *
from hashlib import md5
import datetime


class User(UserMixin, CRUDMixin, Storm):
    __storm_table__ = "users"    
    email = Unicode(default=u'')
    password = Unicode(default=u'')
    nickname = Unicode(default=u'')    
    role = Int(default=2)
    last_seen = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))

    def set_password(self, password):
      self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
      return check_password_hash(self.password, password)

    def avatar(self, size):
      return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    @staticmethod
    def find_by_email(email):
      return store.find(User, User.email == email).one() 
    
    @staticmethod
    def create_table():
      store.execute("CREATE TABLE currency "
                    "(id SERIAL PRIMARY KEY,\
                      email VARCHAR(255) UNIQUE,\
                      nickname VARCHAR(255),\
                      password VARCHAR(255),\
                      role SMALLINT,\
                      last_seen TIMESTAMP,\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX currency_email_idx ON currency USING btree (email);", noresult=True)
      store.execute("CREATE INDEX currency_nickname_idx ON currency USING btree (nickname);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables  WHERE table_catalog='pigeondb' AND table_schema='public' AND table_name='currency');").get_one()
      return result[0]


