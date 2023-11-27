from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from Forms import LoginForm, RegisterForm

# -----  -----  ----- App -----  -----  -----
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"
app.config['SECRET_KEY'] = open("secret_key").readline()  # todo

# -----  -----  ----- DB -----  -----  -----
db = SQLAlchemy()
db.init_app(app)

# -----  -----  ----- Login -----  -----  -----
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

public_address_counter = 0


@login_manager.user_loader
def load_user(user_id):
    from db import User
    return User.query.get(int(user_id))


# -----  -----  ----- APScheduler -----  -----  -----
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
TIME_TO_LIVE = 42  # in minutes


@scheduler.task('cron', id='clear_old_visitor_addrs', minute='*')  # call every minute
def clear_old_visitor_addrs():
    with app.app_context():
        from db import SharedAddresses
        threshold_time = datetime.utcnow() - timedelta(minutes=TIME_TO_LIVE)
        SharedAddresses.query.filter_by(user=0).filter(SharedAddresses.last_updated < threshold_time).delete()
        db.session.commit()


# -----  -----  ----- Helper Functions -----  -----  -----
def format_last_updated(last_updated):
    delta = datetime.utcnow() - last_updated
    days = delta.days
    seconds = delta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif hours > 0:
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif minutes > 0:
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return f"{seconds} {'second' if seconds == 1 else 'seconds'} ago"


# -----  -----  ----- Routes -----  -----  -----
@app.route('/')
def root():
    from db import SharedAddresses

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    if current_user.is_authenticated:
        user_addrs = db.session.execute(
            db.select(SharedAddresses).filter_by(user=current_user.id).order_by(SharedAddresses.last_updated.desc())
        ).scalars()
    else:
        user_addrs = []

    public_addrs = db.session.execute(
        db.select(SharedAddresses).filter_by(user=0).order_by(SharedAddresses.last_updated.desc()).limit(42)
    ).scalars()

    return render_template(
        "index.html",
        ip_addr=ip_addr,
        user=current_user,
        user_addrs=user_addrs,
        public_addrs=public_addrs,
        format_last_updated=format_last_updated
    )


@app.route('/now')
def now():
    """Teilt Ip sofort"""
    from db import SharedAddresses
    global public_address_counter
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_addr = request.environ['REMOTE_ADDR']
    else:
        ip_addr = request.environ['HTTP_X_FORWARDED_FOR']  # if behind a prox

    if current_user.is_authenticated:
        shared_addr = SharedAddresses.query.filter_by(user=current_user.id, device_name="").first()

        if shared_addr is None:
            # create new device
            shared_addr = SharedAddresses(user=current_user.id, device_name="", address=ip_addr, last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update old device
            shared_addr.address = ip_addr
            shared_addr.last_updated = func.now()
            db.session.commit()
    else:
        shared_addr = SharedAddresses.query.filter_by(user=0, address=ip_addr).first()
        if shared_addr is None:
            # create new device
            public_address_counter += 1
            shared_addr = SharedAddresses(user=0, device_name=str(public_address_counter), address=ip_addr, last_updated=func.now())
            db.session.add(shared_addr)
            db.session.commit()
        else:
            # update time
            shared_addr.last_updated = func.now()
            db.session.commit()

    return redirect(url_for('root'))


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
        login_user(new_user, remember=True)
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
                login_user(user, remember=True)
                return redirect(url_for('root'))  # todo: maybe chane to /now
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


@app.route('/impressum')
def impressum():
    """Impressum"""
    return render_template("impressum.html")


# -----  -----  ----- Main -----  -----  -----

if __name__ == '__main__':
    app.run(debug=True)
