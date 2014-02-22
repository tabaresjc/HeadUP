from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
from app.categories.models import Category
from app import store
import datetime
import re


class DbInit(object):
    @classmethod
    def init_db(cls):
        user = User.create()
        user.name = u'Juan Tabares'
        user.nickname = u'jctt'
        user.set_password(u'admin123456')
        user.role = 1
        user.email = u'juan.ctt@live.com'
        user.last_seen = datetime.datetime.utcnow()
        user.save()
        DbInit.init_categories()

    @classmethod
    def init_categories(cls):
        print "*******************************************"
        category = Category.create()
        category.name = u'Uncategorized'
        category.slug = u'uncategorized'
        category.description = u'Fallback category or standard category'
        category.save()

    @classmethod
    def create_posts(cls):
        print "*******************************************"
        user = User.get_by_id(1)
        if not user is None:
            for i in range(1, 51):
                print 'creating post # %s' % i
                post = Post.create()
                post.title = unicode('Title %s' % i)
                post.body = unicode('Body %s' % i)
                post.user = user
                post.save()
            print "Created Dummy Posts for %r" % user

        print "*******************************************"
        user = User.get_by_id(2)
        if not user is None:
            for i in range(1, 51):
                print 'creating post # %s' % i
                post = Post.create()
                post.title = unicode('Title %s' % i)
                post.body = unicode('Body %s' % i)
                post.user = user
                post.save()
            print "Created Dummy Posts for %r" % user

    @classmethod
    def normalize_posts_url(cls):
        posts = store.find(Post)
        for post in posts:
            post.slug = re.sub('[^a-zA-Z0-9]', '_', post.title).lower()
            print post.slug
        store.commit()
