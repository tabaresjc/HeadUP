

class ProfileView(object):

    __json_meta__ = [
        'id',
        'nickname',
        'profile_picture_url'
    ]

    def __init__(self, user):
        self.id = user.id
        self.nickname = user.nickname
        self.profile_picture_url = user.profile_picture_url
