import argparse
import sys
from flask import Flask, send_from_directory
from pymongo.server_api import ServerApi
from pywebio.platform.flask import webio_view, start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import hold
from PIL import Image, ImageFilter
from passlib.hash import pbkdf2_sha256
import pymongo
import dns

app = Flask(__name__)

client = pymongo.MongoClient(
    "mongodb+srv://jlord:M0ng0DB@cluster0.lcjq9.mongodb.net/UserInfo?retryWrites=true&w=majority",
    server_api=ServerApi('1'))
db = client.LoginInfo
coll = db.UserData

@app.route('/')
def register():
    # TODO: define more strict input validation using regex
    popup("Welcome", [
        put_text("Welcome to the application. Please register or login to continue."),
        put_buttons(["Okay"], onclick=lambda _: close_popup())
    ])
    credentials = input_group("Registration Information", [
        input("Email", name="email",
              placeholder="Enter your email address",
              required=True
              ),
        input("Username", name="username",
              placeholder="Enter your desired username",
              required=True
              ),
        input("Password", name="password",
              type=PASSWORD,
              placeholder="Enter your password",
              help_text="Password must be at least 6 characters long.",
              required=True
              ),
    ])
    if not coll.find_one({"username": credentials.get("username")}) and not coll.find_one({"email": credentials.get("email")}):
        credstodb = {
            'email': credentials.get("email"),
            'username': credentials.get("username"),
            'password': pbkdf2_sha256.hash(credentials.get("password"))
        }
        coll.insert_one(credstodb)

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(register, port=args.port)