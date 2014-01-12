from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
from app.categories.models import Category
from app import store
import datetime
import re


class DbInit(object):
    @staticmethod
    def init_db():
        user = User.create()
        user.name = u'Juan Tabares'
        user.nickname = u'jctt'
        user.set_password(u'admin123456')
        user.role = 1
        user.email = u'juan.ctt@live.com'
        user.last_seen = datetime.datetime.utcnow()
        user.save()
        print "Created user %r" % user
        user1 = User.create()
        user1.name = u'Mrs. Arnaldo Wyman'
        user1.nickname = u'arnaldo'
        user1.set_password(u'admin123456')
        user1.email = u'example-2@railstutorial.org'
        user1.last_seen = datetime.datetime.utcnow()
        user1.save()
        print "Created user %r" % user1

    @staticmethod
    def init_categories():
        print "*******************************************"
        category = Category.create()
        category.name = u'Uncategorized'
        category.slug = u'uncategorized'
        category.description = u'Fallback category or standard category'
        category.save()

    @staticmethod
    def create_db():
        # Posts
        if not Post.exist_table():
            Post.create_table()
            print "Created Table [Post]"
        else:
            print "Table [Post] already exist"

        # Comments
        if not Comment.exist_table():
            Comment.create_table()
            print "Created Table [Comment]"
        else:
            print "Table [Comment] already exist"

        # Categories
        if not Category.exist_table():
            Category.create_table()
            print "Created Table [Category]"
            DbInit.init_categories()
        else:
            print "Table [Category] already exist"

        # Users
        if not User.exist_table():
            User.create_table()
            print "Created Table [User]"
            DbInit.init_db()
        else:
            print "Table [User] already exist"

    @staticmethod
    def create_posts():
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

    @staticmethod
    def normalize_posts_url():
        posts = store.find(Post)
        for post in posts:
            post.slug = re.sub('[^a-zA-Z0-9]', '_', post.title).lower()
            print post.slug
        store.commit()
