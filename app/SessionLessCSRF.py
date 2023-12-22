from app import app
from wtforms.csrf.core import CSRF
from datetime import timedelta, datetime
from hashlib import sha256


class SessionLessCSRF(CSRF):
    """
    Generate a CSRF token based on the user's IP. I am probably not very secure, so don't use me.
    https://wtforms.readthedocs.io/en/3.1.x/csrf/
    """

    def setup_form(self, form):
        self.csrf_context = form.meta.csrf_context
        return super(SessionLessCSRF, self).setup_form(form)

    def generate_csrf_token(self, csrf_token):
        time = datetime.now() + timedelta(hours=1)
        timestamp = str(int(time.timestamp()))
        token = sha256((app.config['CSRF_SECRET_KEY'] + self.csrf_context + timestamp).encode()).hexdigest()
        return token + timestamp

    def validate_csrf_token(self, form, field):
        token = field.data[:64]
        timestamp = field.data[64:]
        cmp_token = sha256((app.config['CSRF_SECRET_KEY'] + self.csrf_context + timestamp).encode()).hexdigest()
        if token != cmp_token:
            raise ValueError('Invalid CSRF')

        if datetime.now() > datetime.fromtimestamp(int(timestamp)):
            raise TimeoutError('CSRF Token to old')