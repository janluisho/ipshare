from uuid import UUID, uuid4
from app import app, db
from flask_login import UserMixin


# sqlalchemy.exc.InvalidRequestError: remove views and login_views import in app temporarily
class User(db.Model, UserMixin):
    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    alternative_id: db.Mapped[UUID] = db.mapped_column(db.UUID, unique=True, nullable=False, default=uuid4())
    name: db.Mapped[str] = db.mapped_column(db.String(69), unique=True)
    password: db.Mapped[str] = db.mapped_column(db.String(69))
    # The salt is stored in the password field as well.
    remember: db.Mapped[bool] = db.mapped_column(db.Boolean())

    def get_id(self):
        return self.alternative_id


class SharedAddresses(db.Model):
    user: db.Mapped[int] = db.mapped_column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    device_name: db.Mapped[str] = db.mapped_column(db.String(420), primary_key=True)
    address: db.Mapped[str] = db.mapped_column(db.String(420))
    last_updated: db.Mapped[db.DateTime] = db.mapped_column(db.DateTime)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # add a user for visitors
        db.session.add(User(id=0, name="VISITORS", password="", remember=False))
        db.session.commit()
