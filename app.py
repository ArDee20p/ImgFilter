import argparse
from flask import Flask
from pywebio.platform.flask import start_server
import frontend.register as register


app = Flask(__name__)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(register, port=args.port)