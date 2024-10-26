from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username, password, profile):
        self.id = id
        self.username = username
        self.password = password
        self.profile = profile
