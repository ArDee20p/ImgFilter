import os
from flask import Flask, render_template

from app.login import login_bp
from app.register import register_bp

app = Flask(__name__)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)


@app.route('/')
def welcome():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
