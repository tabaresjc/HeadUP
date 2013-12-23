from app.users.models import User
from app.posts.models import Post
from app.comments.models import Comment
import datetime

class DbInit(object):
	@staticmethod
	def init_db():
		user = User.create()
		user.name = u'Juan Tabares'
		user.nickname = u'jctt'
		user.set_password(u'admin123456')
		user.role = 1
		user.email = u'juan.ctt@live.com'
		user.last_seen = datetime.datetime.now()
		user.save()

		user1 = User.create()
		user1.name = u'Mrs. Arnaldo Wyman'
		user1.nickname = u'arnaldo'
		user1.set_password(u'admin123456')
		user1.email = u'example-2@railstutorial.org'
		user1.last_seen = datetime.datetime.now()
		user1.save()

	@staticmethod
	def create_db():
		# Posts
		if not Post.exist_table():
			Post.create_table()

		# Comments
		if not Comment.exist_table():
			Comment.create_table()

		# Users
		if not User.exist_table():
			User.create_table()
			DbInit.init_db()

	@staticmethod
	def create_posts():
		user = User.get_by_id(1)
		for i in range(1, 51):
			print 'creating post # %s' %i
			post = Post.create()
			post.title = unicode('Title %s' % i)
			post.body = unicode('Body %s' % i)
			post.user = user
			post.save()	