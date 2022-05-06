import os
from os.path import join, dirname, realpath

import flask_login
from flask import Flask
from flask_mongoengine import MongoEngine
# import pymongo
# from pymongo.server_api import ServerApi


ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}
INPUT_FILENAME = ''


app = Flask(__name__, template_folder='./templates')
app.config['MONGODB_SETTINGS'] = {
    'host': "mongodb+srv://jlord:M0ng0DB@cluster0.lcjq9.mongodb.net/UserInfo?retryWrites=true&w=majority"
}
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'a0bgF^P(m*jy^iQ$jntTCxLp)raqqpAG'
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), 'static\\uploads\\')
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from backend import routes
