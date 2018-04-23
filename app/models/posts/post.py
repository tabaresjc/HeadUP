# -*- coding: utf8 -*-

from flask_login import current_user
from app import sa
from app.models import Base
from app.helpers import ModelHelper, MutableObject
import datetime
import base64


class Post(Base, sa.Model, ModelHelper):

    __tablename__ = 'posts'

    __json_meta__ = ['id',
                     'title',
                     'body',
                     'extra_body',
                     'user',
                     'status',
                     'lang',
                     'cover_picture',
                     'category',
                     'anonymous']

    POST_PUBLIC = 0x001
    POST_DRAFT = 0x100
    POST_HIDDEN = 0x800

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(255))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id',
                                                  ondelete='CASCADE',
                                                  onupdate='NO ACTION'))
    category_id = sa.Column(sa.Integer, sa.ForeignKey('categories.id',
                                                      ondelete='CASCADE',
                                                      onupdate='NO ACTION'))
    status = sa.Column(sa.Integer, default=1, index=True, nullable=False)
    lang = sa.Column(sa.String(4), default='en', index=True, nullable=False)
    anonymous = sa.Column(sa.SmallInteger)
    score = sa.Column(sa.Numeric(20, 7),
                      default=0,
                      index=True,
                      nullable=False,
                      server_default='0')
    attr = sa.Column(MutableObject.get_column())
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    comments = sa.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):  # pragma: no cover
        return '<Post %r>' % (self.title)

    @property
    def body(self):
        return self.get_attribute('body')

    @body.setter
    def body(self, value):
        return self.set_attribute('body', value)

    @property
    def extra_body(self):
        return self.get_attribute('extra_body')

    @extra_body.setter
    def extra_body(self, value):
        return self.set_attribute('extra_body', value)

    @property
    def cover_picture(self):
        from app.models import Picture
        return Picture.get_by_id(self.cover_picture_id)

    @property
    def cover_picture_id(self):
        return self.get_attribute('cover_picture_id', 0)

    @cover_picture_id.setter
    def cover_picture_id(self, value):
        return self.set_attribute('cover_picture_id', value)

    @property
    def page_views(self):
        return self.get_attribute('page_views', 1)

    @page_views.setter
    def page_views(self, value):
        return self.set_attribute('page_views', value)

    @property
    def save_count(self):
        return self.get_attribute('save_count', 1)

    @save_count.setter
    def save_count(self, value):
        return self.set_attribute('save_count', value)

    @property
    def votes(self):
        return self.get_attribute('votes', 0)

    @votes.setter
    def votes(self, value):
        return self.set_attribute('votes', value)

    @property
    def down_votes(self):
        return self.get_attribute('down_votes', 0)

    @down_votes.setter
    def down_votes(self, value):
        return self.set_attribute('down_votes', value)

    @property
    def editor_version(self):
        return self.get_attribute('editor_version', 0)

    @editor_version.setter
    def editor_version(self, value):
        return self.set_attribute('editor_version', value)

    @property
    def old_status(self):
        return self.get_attribute('old_status', self.POST_DRAFT)

    @old_status.setter
    def old_status(self, value):
        return self.set_attribute('old_status', value)

    @property
    def is_hidden(self):
        return self.status == self.POST_HIDDEN

    @property
    def is_draft(self):
        return self.status == self.POST_DRAFT

    @property
    def comment_list(self):
        if not hasattr(self, '_comment_list'):
            data = dict([(item.id, item) for item in self.comments])

            for comment in self.comments:
                comment.children = []
                if comment.comment_id and comment.comment_id in data:
                    data[comment.comment_id].children.append(comment)
            self._comment_list = [c for c in self.comments if not c.comment_id]
        return self._comment_list

    def is_mine(self):
        return (current_user.is_authenticated and
                self.user.id == current_user.id)

    def can_edit(self):
        return (current_user.is_authenticated and
                (self.user.id == current_user.id or current_user.is_admin))

    def update_score(self, page_view=0, vote=0, down_vote=0):
        from app.models import Feed

        scale = 10

        if page_view > 0:
            self.page_views = self.page_views + page_view

        if vote > 0:
            self.votes = self.votes + vote

        if down_vote > 0:
            self.down_votes = self.down_votes + down_vote

        self.score = Feed.score(page_views=self.page_views,
                                ups=self.votes,
                                downs=self.down_votes,
                                date=self.created_at)

    @property
    def encoded_id(self):
        return base64.b64encode(bytes('%s' % self.id)).encode('hex')

    @classmethod
    def decode_id(cls, encodedValue):
        return long(base64.b64decode(encodedValue.decode('hex')))

    @classmethod
    def minimun_date(cls):
        return datetime.datetime(1, 1, 1, 0, 0, 0, 0)

    @classmethod
    def current_date(cls):
        return datetime.datetime.utcnow()

    @classmethod
    def get_status_list(cls):
        return [(cls.POST_DRAFT, "Private"), (cls.POST_PUBLIC, "Public")]

    @classmethod
    def get_language_list(cls):
        import config
        return [(value, text) for value, text in config.LANGUAGES.iteritems()]

    @classmethod
    def posts_by_user(cls,
                      user_id,
                      limit=10,
                      page=1,
                      status=POST_PUBLIC,
                      orderby='created_at',
                      desc=True):
        query = cls.query.filter_by(user_id=user_id, status=status)

        count = query.count()
        records = []
        if count:
            sort_by = '%s %s' % (orderby, 'DESC' if desc else 'ASC')
            records = query.order_by(sa.text(sort_by)) \
                .offset((page - 1) * limit) \
                .limit(limit)
        return records, count
