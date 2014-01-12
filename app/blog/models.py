from app import store
from storm.locals import *
from app.posts.models import Post
from app.comments.models import Comment


class Search(object):
    @staticmethod
    def search_post(keyword, limit=10, page=1):
        count = 0
        records = store.find(Post, Or(
            Post.title.like(u'%' + keyword + u'%', case_sensitive=False),
            Post.body.like(u'%' + keyword + u'%', case_sensitive=False)
        ))
        count = records.count()
        records = records.order_by(Desc(Post.id)).config(limit=limit, offset=(page - 1) * limit)
        return records, count


# Get stats and values for the widgets of the blog
def get_stat(value):
    if value == 4:
        last_post, count = Post.pagination()
        return last_post
    elif value == 5:
        last_comments, count = Comment.pagination()
        return last_comments
    else:
        return 0
