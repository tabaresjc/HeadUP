from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from app import database, store
from storm.locals import *
import datetime

"""
Class Users
"""
class User(Storm):
    __storm_table__ = "users"
    __storm_primary__ = "id"
    id = Int()
    email = Unicode(default=u'')
    password = Unicode(default=u'')
    nickname = Unicode(default=u'')    
    role = Int()
    last_seen = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    created_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))

    def set_password(self, password):
      self.password = unicode(generate_password_hash(password))

    def check_password(self, password):
      return check_password_hash(self.password, password)
    
    # Required by Flask-login extension
    def is_authenticated(self):
      return True

    # Required by Flask-login extension
    def is_active(self):
      return True

    # Required by Flask-login extension
    def is_anonymous(self):
      return False

    # Required by Flask-login extension
    def get_id(self):
      return unicode(self.id)

    def avatar(self, size):
      return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
