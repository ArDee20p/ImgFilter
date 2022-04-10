from flask import Blueprint, session, redirect

login_bp = Blueprint('login', __name__)


@login_bp.route('/login')
def login():
    return 'Hello World!'
