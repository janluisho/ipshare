from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# -----  -----  ----- App -----  -----  -----
app = Flask(__name__)
app.config.from_object('config')

# -----  -----  ----- DB -----  -----  -----
db = SQLAlchemy()
db.init_app(app)

# -----  -----  ----- Includes -----  -----  -----
from app.APScheduler import scheduler
from app import views
from app import login_views

