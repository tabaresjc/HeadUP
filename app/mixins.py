from app import store
from storm.locals import *
import datetime

class CRUDMixin(object):
    __storm_primary__ = "id"
    id = Int()

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, basestring) and id.isdigit(),
             isinstance(id, (int, float))),
        ):
            return store.find(cls, cls.id == int(id)).one() 
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        if hasattr(instance,'created_at'):
            setattr(instance, 'created_at', datetime.datetime.now())
        if hasattr(instance,'modified_at'):
            setattr(instance, 'modified_at', datetime.datetime.now())            
        return instance

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        store.add(self)       
        if commit:
            if hasattr(self,'modified_at'):
                setattr(self, 'modified_at', datetime.datetime.now())
            store.commit()
        return self

    def delete(self, commit=True):
        store.find(cls, id == self.id).remove()
        return commit and store.commit()