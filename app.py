from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"


db = SQLAlchemy()
db.init_app(app)


@app.route('/')
def root():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    return render_template("index.html", ip_addr=ip_addr)


@app.route('/now')
def now():
    """Teilt Ip sofort"""
    return "todo"


@app.route('/register')
def register():
    """Account Erstellen"""
    return "todo"


@app.route('/signin')
def signin():
    """Login"""
    return "todo"


@app.route('/impressum')
def impressum():
    """Impressum"""
    return render_template("impressum.html")


if __name__ == '__main__':
    app.run()
