import flask_login
from flask import Flask
from flask_mongoengine import MongoEngine
# import pymongo
# from pymongo.server_api import ServerApi

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': "mongodb+srv://jlord:M0ng0DB@cluster0.lcjq9.mongodb.net/UserInfo?retryWrites=true&w=majority"
}
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'a0bgF^P(m*jy^iQ$jntTCxLp)raqqpAG'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from backend import routes
