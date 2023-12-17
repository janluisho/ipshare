from uuid import UUID, uuid4
from flask import redirect, url_for, flash, render_template
from flask_login import login_user, login_required, fresh_login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from app.Forms import RegisterForm, LoginForm, ChangePseudonymForm, ChangePasswordForm
from app import app, db, limiter
from db import User

DISTINGUISH_NAME_PW_WRONG = True

# -----  -----  ----- Login -----  -----  -----
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    return User.query.filter_by(alternative_id=user_id).first()
    # see: https://flask-login.readthedocs.io/en/latest/#alternative-tokens
    # return User.query.get(int(user_id))


# -----  -----  ----- Views -----  -----  -----


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5/day", methods=['POST'])
def register():
    """Account Erstellen"""
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            flash('This PSEUDONYM is already in use', 'error')
            form.name.render_kw.update({"class": "user-or-pw-wrong"})
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(name=form.name.data, password=hashed_password, remember=form.remember.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=form.remember.data)
            return redirect(url_for('root'))

    return render_template('register.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
@limiter.limit("10/day;5/hour;3/minute", methods=['POST'])  # deduct_when=lambda response: response.status_code != 302)
def signin():
    """Login"""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=user.remember)
                return redirect(url_for('root'))  # todo: maybe change to /now
            elif DISTINGUISH_NAME_PW_WRONG:
                flash('Invalid password provided', 'error')
                form.name.render_kw.update({"class": ""})
                form.password.render_kw.update({"class": "user-or-pw-wrong"})
            else:
                flash('Invalid pseudonym or password provided', 'error')
                form.name.render_kw.update({"class": "user-or-pw-wrong"})
                form.password.render_kw.update({"class": "user-or-pw-wrong"})
        else:
            flash('Invalid pseudonym or password provided', 'error')
            form.name.render_kw.update({"class": "user-or-pw-wrong"})
            form.password.render_kw.update({"class": "user-or-pw-wrong"})
    else:
        form.name.render_kw.update({"class": ""})
        form.password.render_kw.update({"class": ""})
    return render_template('signin.html', form=form)


@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('root'))


@app.route('/me', methods=['GET', 'POST'])
@fresh_login_required
def me():
    pseudonym_form = ChangePseudonymForm()
    password_form = ChangePasswordForm()

    if pseudonym_form.validate_on_submit():
        user = User.query.filter_by(name=pseudonym_form.name.data).first()
        if not user:
            current_user.name = pseudonym_form.name.data
            db.session.commit()
            logout_user()
            return redirect(url_for('signin'))
        elif user.id == current_user.id:
            flash('You already have that PSEUDONYM', 'warning')
            pseudonym_form.name.render_kw.update({"class": "user-or-pw-wrong"})
        else:
            flash('This PSEUDONYM is already in use', 'error')
            pseudonym_form.name.render_kw.update({"class": "user-or-pw-wrong"})

    if password_form.validate_on_submit():
        current_user.password = bcrypt.generate_password_hash(password_form.password.data)
        current_user.alternative_id = uuid4()  # invalidate tokens see: https://flask-login.readthedocs.io/en/latest/#alternative-tokens
        db.session.commit()
        logout_user()
        return redirect(url_for('signin'))

    return render_template(
        'me.html',
        current_user=current_user,
        pseudonym_form=pseudonym_form,
        password_form=password_form
    )


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


@login_manager.needs_refresh_handler
def refresh():
    return redirect(url_for('signin'))
