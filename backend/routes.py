import re
from flask_login import current_user, login_user, login_required, logout_user
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from werkzeug.security import generate_password_hash, check_password_hash
from backend.forms import RegForm, LoginForm
from backend.models import User, Image
from flask import request, redirect, render_template, url_for, flash
from backend import app


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        message = ''
        user = request.form.get("username")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = User.objects(username=user).first()
        email_found = User.objects(email=email).first()
        if user_found:
            message = ('There is already a user with that name: %s %s %s',
                       user_found.username, user_found.email, user_found.password)
            return render_template('register.html', message=message)
        elif email_found:
            message = 'This email has already been registered.'
            return render_template('register.html', message=message)
        elif password1 != password2:
            message = 'Passwords must match!'
            return render_template('register.html', message=message)
        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            user_input = User()
            user_input.username = user
            user_input.email = email
            user_input.password = hashed
            user_input.save()
            return redirect(url_for('gallery'))
    return render_template('register.html')
    # form = RegForm()
    # if request.method == 'POST':
    #     if form.validate():
    #         existing_user = User.objects(email=form.email.data).first()
    #         if existing_user is None:
    #             hashpass = generate_password_hash(form.password.data, method='sha256')
    #             newuser = User(form.email.data, form.username.data, hashpass).save()
    #             login_user(newuser)
    #             return redirect(url_for('gallery'))
    # return render_template('login.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    message = ''
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = User.objects(email=email).first()
        if email_found:
            if pbkdf2_sha256.verify(password.encode('utf-8'), email_found.password):
                user = User()
                user.email = email_found.email
                user.username = email_found.username
                user.password = email_found.password
                login_user(user)
                return redirect(url_for('gallery'))
            else:
                message = 'Wrong password.'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found.'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)
    # form = LoginForm()
    # if request.method == 'POST':
    #     if form.validate():
    #         check_user = User.objects(email=form.email.data).first()
    #         if check_user:
    #             if check_password_hash(check_user['password'], form.password.data):
    #                 login_user(check_user)
    #                 return redirect(url_for('gallery'))
    # return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


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
    user = User.objects.get(username=username)
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('gallery'))
    userimages = Image.objects(uploader=user["username"])
    return render_template('user.html', user=user, userimages=userimages)


@app.route('/change', methods=['POST'])
@login_required
def changeinfo(username):
    if request.method == "POST":
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        currpword = request.form.get("currentpassword")

        user = User.objects.get(email=email)

        if not pbkdf2_sha256.verify(currpword, user["password"]):
            flash('Please enter your current password to change your login info!')
            return redirect(url_for('changeinfo'))

        if password1 != password2:
            flash('Passwords must match!')
            return redirect(url_for('changeinfo'))

        if not (re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1)):
            flash('Please follow the instructions to create a safer password.')
            return redirect(url_for('changeinfo'))

        if not (re.fullmatch('^[a-zA-Z0-9äöüÄÖÜ]*$', user)):
            flash('Username cannot contain special characters.')
            return redirect(url_for('changeinfo'))
        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            # coll.updateOne({'username': username, 'email': email, 'password': hashed}) TODO: find MongoEngine update data function
            return redirect(url_for('changeinfo'))
    return redirect(url_for('login'))
