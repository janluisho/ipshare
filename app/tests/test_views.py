import time
from datetime import datetime, timedelta
from unittest import TestCase
from flask_login import FlaskLoginClient
from app import app, db
from app.views import format_last_updated
from db import User, SharedAddresses

app.test_client_class = FlaskLoginClient


class TestViews(TestCase):
    def test_format_last_updated(self):
        def format(delta):
            return format_last_updated(datetime.utcnow() - delta)

        self.assertEqual("1 day ago", format(timedelta(days=1)))
        self.assertEqual("1 day ago", format(timedelta(days=1, hours=3, minutes=3)))

        self.assertEqual("2 days ago", format(timedelta(days=2)))
        self.assertEqual("2 days ago", format(timedelta(days=2, hours=3)))

        self.assertEqual("1 hour ago", format(timedelta(hours=1)))
        self.assertEqual("1 hour ago", format(timedelta(hours=1, minutes=3)))

        self.assertEqual("2 hours ago", format(timedelta(hours=2)))
        self.assertEqual("2 hours ago", format(timedelta(hours=2, seconds=3)))

        self.assertEqual("1 minute ago", format(timedelta(minutes=1)))
        self.assertEqual("1 minute ago", format(timedelta(minutes=1, seconds=3)))

        self.assertEqual("2 minutes ago", format(timedelta(minutes=2)))
        self.assertEqual("2 minutes ago", format(timedelta(minutes=2, seconds=1)))

        self.assertEqual("1 second ago", format(timedelta(seconds=1)))
        self.assertEqual("1 second ago", format(timedelta(seconds=1, milliseconds=3)))

        self.assertEqual("2 seconds ago", format(timedelta(seconds=2)))
        self.assertEqual("2 seconds ago", format(timedelta(seconds=2, milliseconds=14)))

    def test_root(self):
        with app.app_context():
            user = User.query.filter_by(id=0).first()
            with app.test_client(user=user) as client:
                response = client.get("/")
                self.assertEqual(200, response.status_code)
                self.assertIn(b'<a href="/impressum"', response.data, "Missing Link to Impressum.")
                self.assertFalse(response.headers.getlist('Set-Cookie'), "No Cookie policy violated")
        self.fail("More to testing needed")

    def test_now(self):
        with app.app_context():
            with app.test_client() as client:
                self.assertIsNone(SharedAddresses.query.filter_by(user=0, address="127.0.0.1").first(),
                                  'db not ready for test: delete user=0 address="127.0.0.1" from shared_addresses.')

                # test redirect and No Cookie policy
                response = client.get("/now")
                self.assertEqual(302, response.status_code)
                self.assertFalse(response.headers.getlist('Set-Cookie'), "No Cookie policy violated")

                response = client.get("/now", follow_redirects=True)
                self.assertEqual(200, response.status_code)
                self.assertEqual(1, len(response.history))
                self.assertEqual("/", response.request.path)
                self.assertFalse(response.headers.getlist('Set-Cookie'), "No Cookie policy violated")

                # test address sharing
                addr = SharedAddresses.query.filter_by(user=0, address="127.0.0.1").first()
                self.assertIsNotNone(addr, "address not in db")
                t1 = addr.last_updated

                time.sleep(1)
                client.get("/now")

                addr = SharedAddresses.query.filter_by(user=0, address="127.0.0.1").first()
                self.assertIsNotNone(addr,"address not in db")
                t2 = addr.last_updated

                self.assertLess(t1, t2, "time not updated")

                # delete address from db
                SharedAddresses.query.filter_by(user=0, address="127.0.0.1").delete()
                db.session.commit()
                self.assertIsNone(SharedAddresses.query.filter_by(user=0, address="127.0.0.1").first(),
                                  "address deletion failed")

    def test_impressum(self):
        with app.app_context():
            with app.test_client() as client:
                response = client.get("/impressum")
                self.assertEqual(200, response.status_code)
                self.assertIn(b'<h1>Impressum</h1>', response.data)
                self.assertIn(b'Jan Luis Holtmann', response.data)
                self.assertIn(b'Augsburg', response.data)
                self.assertIn(b'<h1>Kontakt:</h1>', response.data)
                self.assertIn(b'Telefon: +49 (0)163-6955847', response.data)
                self.assertIn(b'webmaster@janluis.de', response.data)
                self.assertIn(b'Dies ist eine nicht kommerzielle Seite.', response.data)
                self.assertFalse(response.headers.getlist('Set-Cookie'), "No Cookie policy violated")
