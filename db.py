from app import app, db
from sqlalchemy.sql import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    name: db.Mapped[str] = db.mapped_column(db.String(69), unique=True)
    password: db.Mapped[str] = db.mapped_column(db.String(69))
    # The salt is stored in the password field as well.


class SharedAddresses(db.Model):
    user: db.Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    device_name: db.Mapped[str] = db.mapped_column(db.String(420), primary_key=True)
    address: db.Mapped[str] = db.mapped_column(db.String(420))
    last_updated: db.Mapped[db.DateTime] = db.mapped_column(db.DateTime, server_default=func.now(), onupdate=func.now())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
