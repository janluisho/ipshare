from flask import Flask, render_template, request, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"


db = SQLAlchemy()
db.init_app(app)


@app.route('/')
def hello_world():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    return render_template("index.html", ip_addr=ip_addr)


if __name__ == '__main__':
    app.run()
