import pymongo
from pymongo.server_api import ServerApi

client = pymongo.MongoClient(
    "mongodb+srv://jlord:M0ng0DB@cluster0.lcjq9.mongodb.net/UserInfo?retryWrites=true&w=majority",
    server_api=ServerApi('1'))
db = client.LoginInfo
coll = db.UserData
