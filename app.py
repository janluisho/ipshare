from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from Forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"
app.config['SECRET_KEY'] = open("secret_key").readline()  # todo

db = SQLAlchemy()
db.init_app(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    from db import User
    return User.query.get(int(user_id))


@app.route('/')
def root():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    return render_template("index.html", ip_addr=ip_addr, user=current_user)


@app.route('/now')
def now():
    """Teilt Ip sofort"""
    return "todo"


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Account Erstellen"""
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        from db import User
        new_user = User(name=form.name.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('signin'))

    return render_template('register.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Login"""
    form = LoginForm()
    if form.validate_on_submit():
        from db import User
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('root'))  # todo: maybe chane to /now
    # todo: login failed
    return render_template('signin.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('root'))


@app.route('/impressum')
def impressum():
    """Impressum"""
    return render_template("impressum.html")


if __name__ == '__main__':
    app.run(debug=True)
