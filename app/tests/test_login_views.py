from unittest import TestCase

from app import db, app
from app.login_views import load_user
from db import User


class TestLoginViews(TestCase):
    def test_load_user(self):
        with app.app_context():
            # create test user in db:
            new_user = User(name="TestUser", password="testuser_password", remember=False)
            db.session.add(new_user)
            db.session.commit()

            # get user by alternative_id
            self.assertEqual(new_user, load_user(new_user.alternative_id))

            # delete test user
            db.session.delete(new_user)
            db.session.commit()

    def test_redirect_next(self):
        self.fail()

    def test_register(self):
        self.fail()

    def test_signin(self):
        self.fail()

    def test_signout(self):
        self.fail()

    def test_me(self):
        self.fail()

    def test_unauthorized_handler(self):
        self.fail()

    def test_refresh(self):
        self.fail()
