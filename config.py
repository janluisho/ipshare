import datetime

SQLALCHEMY_DATABASE_URI = "sqlite:///database.sqlite"
SECRET_KEY = "secret_key"  # open("secret_key").readline()  # todo
CSRF_SECRET_KEY = "csrf_secret_key"  # todo
JWT_SECRET_KEY = "jwt_secret_key"  # todo
VISITOR_PASSWORD = "visitor_password"  # todo
# PERMANENT_SESSION_LIFETIME = 6000
# REMEMBER_COOKIE_DURATION = datetime.timedelta(days=42)
# REMEMBER_COOKIE_DOMAIN =   # todo
# REMEMBER_COOKIE_SAMESITE = True
