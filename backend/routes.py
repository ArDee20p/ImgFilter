import re
import flask
import flask_login
from flask_login import current_user, login_user, login_required, logout_user
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from backend.models import User as User
from flask import request, redirect, render_template, url_for, flash, session
from backend import app, coll, login_manager, db

passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
usernameRegex = "^[a-zA-Z0-9äöüÄÖÜ]*$"


@login_manager.user_loader
def user_loader(email):
    userfind = coll.find_one({"email": email})
    if not userfind:
        return

    user = User(userfind['username'], userfind['email'], userfind['password'])
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    userfind = coll.find_one({"email": email})
    if not userfind:
        return

    user = User(userfind['username'], userfind['email'], userfind['password'])
    return user


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
    if current_user.is_authenticated:
        return redirect(url_for("gallery"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = coll.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if pbkdf2_sha256.verify(password.encode('utf-8'), passwordcheck):
                user = User(email_found['username'], email_val, passwordcheck)
                login_user(user)  # TODO: create cookie to actually make this mean something.
                return redirect(url_for('gallery'))
            else:
                if current_user.is_authenticated:
                    return redirect(url_for("gallery"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html', message='You have been logged out.')


# TODO: create image editing frontend code here
@app.route('/image_editor')
def image_editor():
    return render_template('editor.html')


# TODO: create public image gallery code here
@app.route('/gallery')
@login_required
def gallery():
    return render_template('gallery.html')


@app.route('/user/<username>')
@login_required
def profile(username):
    user = coll.find_one({"username": username})
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('gallery'))
    userimages = coll.find(uploader=user["username"])
    return render_template('user.html', user=user, userimages=userimages)


@app.route('/change', methods=['GET', 'POST'])
@login_required
def changeinfo(username):
    message = ''
    if request.method == "POST":
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        currpword = request.form.get("currentpassword")

        user = coll.find_one({"email": email})

        if not pbkdf2_sha256.verify(currpword, user["password"]):
            message = 'Please enter your current password to change your login info!'
            return render_template('change.html', message=message)
        if password1 != password2:
            message = 'Passwords must match!'
            return render_template('change.html', message=message)
        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            coll.updateOne({'username': username, 'email': email, 'password': hashed})
            return render_template('login.html')
    return render_template('login.html')