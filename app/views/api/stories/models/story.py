from profile import ProfileView


class StoryView(object):

    __json_meta__ = ['id',
                     'title',
                     'body',
                     'extra_body',
                     'user',
                     'status',
                     'lang',
                     'url',
                     'cover_picture',
                     'cover_picture_id',
                     'created_at',
                     'modified_at',
                     'category',
                     'anonymous',
                     'likes',
                     'is_hidden',
                     'is_editable',
                     'is_owner']

    def __init__(self, story):
        self.id = story.id
        self.title = story.title
        self.body = story.body
        self.extra_body = story.extra_body
        self.user = ProfileView(story.user)
        if story.anonymous:
            self.user = None
        self.status = story.status
        self.lang = story.lang
        self.url = story.url
        self.cover_picture = story.cover_picture
        self.cover_picture_id = story.cover_picture_id
        self.created_at = story.created_at
        self.modified_at = story.modified_at
        self.category = story.category
        self.anonymous = story.anonymous
        self.likes = story.likes
        self.is_hidden = story.is_hidden
        self.is_editable = story.is_editable
        self.is_owner = story.is_owner
