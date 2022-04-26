import uuid
from flask_login import UserMixin
from mongoengine import Document, StringField, ImageField, ObjectIdField

from backend import login_manager, db


class Image(Document):
    _id = ObjectIdField()
    uploader = StringField(required=True)
    imagedata = ImageField()
    meta = {'collection': 'ImageInfo'}


class User(UserMixin, db.Document):
    _id = ObjectIdField()
    email = db.StringField(required=True)
    username = db.StringField(required=True)
    password = db.StringField(required=True)
    meta = {'collection': 'LoginInfo'}


@login_manager.user_loader
def user_loader(user_id):
    return User.objects.get(pk=user_id).first()
