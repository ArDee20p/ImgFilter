from flask import Flask, send_from_directory
from pywebio import STATIC_PATH, start_server
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import hold
from PIL import Image, ImageFilter

app = Flask(__name__)


@app.route('/')
def welcome():
    popup("Welcome", [
        put_text("Welcome to the application. Please register or login to continue."),
        put_buttons(["Okay"], onclick=lambda _: close_popup())
    ])

def register():
    credentials = input_group("Registration Information", [
        input("Email", name="email"),
        input("Password", name="password",
        type=PASSWORD,
        placeholder="Enter your password",
        help_text="Password should be at least 6 characters long.",
        required=True
        ),
    ])

#def login():


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(welcome, port=args.port)
