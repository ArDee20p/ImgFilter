import re
from flask import Blueprint, redirect
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pywebio.input import *
from app.database import coll

register_bp = Blueprint('register', __name__)
passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
usernameRegex = "^[a-zA-Z0-9äöüÄÖÜ]*$"


def check_inputs(credentials):
    if not (re.search(passwordRegex, credentials['password'])):
        return 'password', 'Please follow the instructions to create a safer password.'
    if not (re.search(usernameRegex, credentials['username'])):
        return 'username', 'Username cannot contain special characters.'


@register_bp.route('/register')
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