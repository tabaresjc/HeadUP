from flask.ext.login import current_user
from app import store
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
    created_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    modified_at = DateTime(default_factory=lambda: datetime.datetime(1970, 1, 1))
    user = Reference(user_id, User.id)
    post = Reference(post_id, Post.id)
    reply = Reference(comment_id, 'Comment.id')

    def __repr__(self): # pragma: no cover
      return '<Comment %s>' % (self.id)

    def can_edit(self):
      return current_user.is_authenticated and (self.user.id == current_user.id or current_user.is_admin())
    
    @staticmethod
    def safe_delete(comment, recursive=False):
      if comment.replies:
        for c in comment.replies:
          Comment.safe_delete(c, recursive=True)
        replies = store.find(Comment, Comment.comment_id == comment.id)
        replies.remove()
      Comment.delete(comment.id, commit=False)
      if not recursive:
        store.commit()

