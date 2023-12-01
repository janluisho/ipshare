from flask import redirect, url_for, render_template
from flask_login import login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from Forms import RegisterForm, LoginForm
from app import app, db
from db import User

# -----  -----  ----- Login -----  -----  -----
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

public_address_counter = 0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----  -----  ----- Views -----  -----  -----


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Account Erstellen"""
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('signin'))

    return render_template('register.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    """Login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
                return redirect(url_for('root'))  # todo: maybe change to /now
    # todo: login failed
    return render_template('signin.html', form=form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('root'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401
