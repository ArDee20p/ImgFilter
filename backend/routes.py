import glob
import os
import re
from flask_login import login_user, current_user, logout_user
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pymongo import settings
from werkzeug.utils import secure_filename

from backend.image_routines import *
from backend.models import User
from flask import request, redirect, render_template, url_for, send_file
from backend import app, ALLOWED_EXTENSIONS, login_manager


@app.route('/')
def landing():
    return render_template('index.html')


@login_manager.user_loader
def user_loader(email):
    userfind = User.objects(email=email).first()
    if not userfind:
        return

    user = User(userfind['username'], userfind['email'], userfind['password'])
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    userfind = User.objects(email=email).first()
    if not userfind:
        return

    user = User(username=userfind['username'], email=userfind['email'], password=userfind['password'])
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == "POST":
        user = request.form.get("username")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # user_found = coll.find_one({"username": user})
        # email_found = coll.find_one({"email": email})
        user_found = User.objects(username=user).first()
        email_found = User.objects(email=email).first()

        if user_found:
            message = 'There is already a user with that name.'
            return render_template('register.html', message=message)

        elif email_found:
            message = 'This email has already been registered.'
            return render_template('register.html', message=message)

        elif password1 != password2:
            message = 'Passwords must match!'
            return render_template('register.html', message=message)

        elif not (re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1)):
            message = 'Please follow the instructions to create a safer password.'
            return render_template('register.html', message=message)

        elif not (re.fullmatch('^[a-zA-Z0-9äöüÄÖÜ]*$', user)):
            message = 'Username cannot contain special characters.'
            return render_template('register.html', message=message)

        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            user_input = User()
            user_input.username = user
            user_input.email = email
            user_input.password = hashed
            user_input.save()
            # user_input = {'username': user, 'email': email, 'password': hashed}
            # coll.insert_one(user_input)
            return redirect(url_for('login'))

    return render_template('register.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
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


# @login_required
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('login.html', message='You have been logged out.')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


image, slider = None, None
colors = []
width, height = 0, 0


def refresh_parameters(image_path):
    global image, slider, hue_angle, colors, width, height
    image = load_image(image_path)
    slider = get_default_slider()
    width, height = get_image_size(image)
    colors = get_dominant_colors(image_path)


# So preview refreshes with any new change
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


def remove_static_files():
    CLEANUP_FOLDER = os.getcwd() + 'static/uploads/'
    files = glob.glob(CLEANUP_FOLDER)
    for f in files:
        os.remove(f)


# Image editing home
@app.route('/upload', methods=['GET', 'POST'])
def uploadimage():
    global INPUT_FILENAME
    remove_static_files()
    filemessage = "Upload an image..."
    if request.method == 'POST':
        submit_button = request.form.get('submit_button')
        if submit_button == 'upload_image':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)

            file = request.files['file']
            filemessage = secure_filename(file.filename)
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return redirect(request.url)

            if file and allowed_file(file.filename):
                INPUT_FILENAME = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME))
                dupe_image(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), 'copy')
                refresh_parameters(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME))
                return redirect(url_for('uploaded'))

    return render_template('upload.html', filemessage=filemessage)


# Actual Image editing code
@app.route('/uploaded', methods=['GET', 'POST'])
def uploaded():
    global image, slider

    if INPUT_FILENAME:
        if request.method == 'POST':
            # Nav
            original_button = request.form.get('original_button')
            download_button = request.form.get('download_button')
            # Sliders
            enhance_button = request.form.get('enhance_button')
            # Hue
            hue_button = request.form.get('hue_button')
            # Filters
            blur_button = request.form.get('blur_button')
            sharpen_button = request.form.get('sharpen_button')
            edge_button = request.form.get('edge_button')
            smooth_button = request.form.get('smooth_button')
            # Rotate/resize/crop
            rotate_button = request.form.get('rotate_button')
            resize_button = request.form.get('resize_button')
            crop_button = request.form.get('crop_button')

            if original_button:
                dupe_image(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), 'replace')
            if download_button:
                return send_file(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), as_attachment=True)

            if enhance_button:
                slider = {key: float(request.form.get(key)) for key, value in slider.items()}
                apply_enhancers(image, os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), slider)
            if hue_button:
                hue_angle = float(request.form.get('hue_angle'))
                apply_hue_shift(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), hue_angle)

            if blur_button:
                apply_blur(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), blur_button)
            elif sharpen_button:
                apply_sharpen(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), sharpen_button)
            elif edge_button:
                apply_edge_enhance(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), edge_button)
            elif smooth_button:
                apply_smooth(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), smooth_button)

            if rotate_button:
                angle = int(request.form.get('angle'))
                rotate_image(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), angle)
            elif resize_button:
                n_width = int(request.form.get('width'))
                n_height = int(request.form.get('height'))
                resize_image(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), n_width, n_height)
            elif crop_button:
                start_x = int(request.form.get('start_x'))
                start_y = int(request.form.get('start_y'))
                end_x = int(request.form.get('end_x'))
                end_y = int(request.form.get('end_y'))
                crop_image(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME), start_x, start_y, end_x, end_y)

            if any([original_button, hue_button, blur_button, sharpen_button, edge_button, smooth_button, rotate_button, resize_button, crop_button]):
                refresh_parameters(os.path.join(app.config['UPLOAD_FOLDER'], INPUT_FILENAME))

        return render_template('editor.html', slider=slider, colors=colors, width=width, height=height, filename=INPUT_FILENAME)
    else:
        return render_template('editor.html', slider=slider)


# @login_required
@app.route('/gallery')
def gallery():
    images = []
    for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
                images.append(file)
    return render_template('gallery.html', images=images, len=len(images))


# @login_required
@app.route('/user')
def profile():
    return render_template('user.html')


# @login_required
@app.route('/change', methods=['GET', 'POST'])
def changeinfo():
    message = 'Your username cannot be changed after registration.'
    if request.method == "POST":
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        newemail = request.form.get("newemail")
        currpword = request.form.get("currentpassword")

        user = User.objects.get(email=email)
        try:
            email_found = (User.objects.get(email=newemail))
        except:
            email_found = None

        if not pbkdf2_sha256.verify(currpword, user["password"]):
            message = 'Please enter your current password to change your login info!'
            return render_template('change.html', message=message)
        elif email_found:
            message = 'This email has already been registered.'
            return render_template('change.html', message=message)
        elif password1 != password2:
            message = 'Passwords must match!'
            return render_template('change.html', message=message)

        elif (not (re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password1))) and password1 and password2:
            message = 'Please follow the instructions to create a safer password.'
            return render_template('change.html', message=message)
        else:
            hashed = pbkdf2_sha256.hash(password2.encode('utf-8'))
            if newemail and password1:
                message = 'Your email and password have been changed successfully. For your safety, please log in ' \
                          'again. '
                logout_user()
                user.email = newemail
                user.password = hashed
                user.save()
                return render_template('login.html', message=message)
            elif newemail and (not password1):
                message = 'Your email has been changed successfully. For your safety, please log in again.'
                logout_user()
                user.email = newemail
                user.save()
                return render_template('login.html', message=message)
            elif (not newemail) and password1:
                message = 'Your password has been changed successfully. For your safety, please log in again.'
                logout_user()
                user.password = hashed
                user.save()
                return render_template('login.html', message=message)
            else:
                message = 'You did not enter anything to change! If you would like to log in, please go to the login ' \
                          'page. '
                return render_template('change.html', message=message)
    return render_template('change.html', message=message)
