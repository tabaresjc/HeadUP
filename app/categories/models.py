from app import store
from app.mixins import CRUDMixin
from storm.locals import *
import datetime


class Category(CRUDMixin):
    __storm_table__ = "categories"
    
    name = Unicode(default=u'')
    slug = Unicode(default=u'')

    created_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))

    def can_edit(self):
      return current_user and current_user.is_admin()
    
    def __repr__(self):
      return '<Category %s>' % (self.id)

    @staticmethod
    def create_table():
      store.execute("CREATE TABLE categories "
                    "(id SERIAL PRIMARY KEY,\
                      name VARCHAR(50),\
                      slug VARCHAR(255),\
                      created_at TIMESTAMP,\
                      modified_at TIMESTAMP);", noresult=True)
      store.execute("CREATE INDEX categories_slug_idx ON categories USING hash(slug);", noresult=True)
      store.commit()
      return True

    @staticmethod
    def exist_table():
      result = store.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='categories');").get_one()
      return result[0]
