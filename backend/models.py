import uuid
from flask import session
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from backend import coll


class User(UserMixin):

    def __init__(self, username, email, password, _id=None):

        self.username = username
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    @classmethod
    def get_by_username(cls, username):
        data = coll.find_one("users", {"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_email(cls, email):
        data = coll.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = coll.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return check_password_hash(verify_user.password, password)
        return False

    @classmethod
    def registeruser(cls, username, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(username, email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False

    def json(self):
        return {
            "username": self.username,
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        coll.insert("users", self.json())
