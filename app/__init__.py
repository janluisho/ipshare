from flask import Flask, make_response, render_template
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from flask.sessions import SecureCookieSessionInterface, SessionMixin

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


# -----  -----  ----- Custom Session Interface -----  -----  -----
class CustomSessionInterface(SecureCookieSessionInterface):
    """https://pydocbrowser.github.io/flask/latest/flask.sessions.SessionInterface.html"""
    def should_set_cookie(self, app: "Flask", session: SessionMixin) -> bool:
        if not current_user.is_authenticated:
            return False  # don't send a cookie if the user is not authenticated
        return super().should_set_cookie(app, session)


app.session_interface = CustomSessionInterface()


# -----  -----  ----- Includes -----  -----  -----
from app import Socket
from app.APScheduler import scheduler
from app.views import ip_share_views
from app.login_views import login_views
from app.api import api_views
from app.qr import qr_views

app.register_blueprint(ip_share_views)
app.register_blueprint(login_views)
app.register_blueprint(api_views, url_prefix="/v1")
app.register_blueprint(qr_views, url_prefix="/qr")
