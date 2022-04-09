import argparse
from flask import Flask, redirect
from pywebio.platform.flask import start_server
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pywebio.output import *
from pywebio.input import *
import re
from backend.database import coll

app = Flask(__name__)
passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
usernameRegex = "^[a-zA-Z0-9äöüÄÖÜ]*$"


@app.route('/')
def welcome():
    put_text("Welcome to the image editing application. Please register or login to continue."),
    put_buttons(["Login", "Register"], onclick=[redirect('/login'), redirect('/register')])


def check_inputs(credentials):
    if not (re.search(passwordRegex, credentials['password'])):
        return 'password', 'Please follow the instructions to create a safer password.'
    if not (re.search(usernameRegex, credentials['username'])):
        return 'username', 'Username cannot contain special characters.'


@app.route('/register')
def register():
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
              help_text="Password must be at least 8 characters long, and contain at least: one uppercase and "
                        "lowercase letter, one number, and one special character.",
              required=True
              ),
    ], validate=check_inputs, cancelable=True)

    if not coll.find_one({"username": credentials.get("username")}) and not coll.find_one(
            {"email": credentials.get("email")}):
        credstodb = {
            'email': credentials.get("email"),
            'username': credentials.get("username"),
            'password': pbkdf2_sha256.hash(credentials.get("password"))
        }
        coll.insert_one(credstodb)

    return redirect('/login')


@app.route('/login')
def login():
    return 'Hello World!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(welcome, port=args.port, debug=True)