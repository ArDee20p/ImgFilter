import re
import flask
import flask_login
from flask_login import current_user, login_user
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from backend.models import User
from flask import request, redirect, render_template, url_for, flash, session
from backend import app, coll, login_manager, db

passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
usernameRegex = "^[a-zA-Z0-9äöüÄÖÜ]*$"


@login_manager.user_loader
def user_loader(email):
    if not coll.find({"email": email}):
        return

    user = User()
    user.id = email
    return user
#
#
# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if not coll.find({"email": email}):
#         return
#
#     user = User()
#     user.id = email
#     return user


def check_inputs(credentials):
    if not (re.search(passwordRegex, credentials['password'])):
        return 'password', 'Please follow the instructions to create a safer password.'
    if not (re.search(usernameRegex, credentials['username'])):
        return 'username', 'Username cannot contain special characters.'


@app.route('/', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    message = ''
    if "email" in session:
        return redirect(url_for("gallery"))
    if request.method == "POST":
        user = request.form.get("username")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = coll.find_one({"username": user})
        email_found = coll.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name.'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email has already been registered.'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords must match!'
            return render_template('index.html', message=message)
        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            user_input = {'username': user, 'email': email, 'password': hashed}
            coll.insert_one(user_input)

            user_data = coll.find_one({"email": email})
            new_email = user_data['email']

            return render_template('login.html')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("gallery"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = coll.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if pbkdf2_sha256.verify(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('gallery'))
            else:
                if "email" in session:
                    return redirect(url_for("gallery"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    flask_login.logout_user()
    session.pop('email', default=None)
    return 'You have been logged out.'


# TODO: create image editing frontend code here
@app.route('/image_editor')
def image_editor():
    return 'Hello from Image Editor!'


# TODO: create public image gallery code here
@app.route('/gallery')
def gallery():
    return 'Hello from Gallery!'


# TODO: create user profile/private image gallery code here
@app.route('/user/<username>')
def profile(user):
    return 'Hello from Userpage of ' + user
