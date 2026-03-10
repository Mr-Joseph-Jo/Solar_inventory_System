from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role
