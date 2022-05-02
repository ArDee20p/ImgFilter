from mongoengine import Document, StringField, ImageField, ObjectIdField
from flask_login import UserMixin
from backend import db


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
