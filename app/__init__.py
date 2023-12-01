from flask import Flask, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

# -----  -----  ----- App -----  -----  -----
app = Flask(__name__)
app.config.from_object('config')

# -----  -----  ----- DB -----  -----  -----
db = SQLAlchemy()
db.init_app(app)

# -----  -----  ----- Limiter -----  -----  -----

def default_error_responder(request_limit: RequestLimit):
    return make_response(render_template("ratelimit.html", request_limit=request_limit),429)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["420 per day", "42 per hour"],
    storage_uri="memory://",
    on_breach=default_error_responder,
)


# -----  -----  ----- Includes -----  -----  -----
from app.APScheduler import scheduler
from app import views
from app import login_views

