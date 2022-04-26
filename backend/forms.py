from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, EmailField
from wtforms.validators import InputRequired, Email, Length, EqualTo


class RegForm(FlaskForm):
    email = EmailField('Email Address',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8), EqualTo('confirm', message='Passwords must match!')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField('Email Address',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField()
