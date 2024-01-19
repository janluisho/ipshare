import jwt
from unittest import TestCase

from sqlalchemy import func

from app import app, db
from db import SharedAddresses, User

class Test(TestCase):
    def setUp(self):
        self.user_id = -1

        with app.app_context():
            user = User(
                id=self.user_id,
                name="Test User",
                password="Test User Password",
                remember=0
            )
            db.session.add(user)
            db.session.commit()

            self.alternative_id = user.alternative_id.hex()

    def tearDown(self):
        with app.app_context():
            user = User.query.filter_by(id=self.user_id).first()
            db.session.delete(user)
            db.session.commit()

    def test_apiv1_get_auth(self):
        with app.app_context():
            with app.test_client() as client:
                # No Authorization at all
                self.assertEqual(401, client.get("/v1").status_code)
        
                # Bearer missing
                encoded = jwt.encode({"some": "payload"}, "asdf", algorithm="HS256")
                headers = {"Authorization": f"{encoded}"}
                self.assertEqual(401, client.get("/v1", headers=headers).status_code)
        
                # Invalid Signature
                encoded = jwt.encode({"some": "payload"}, "asdf", algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}
                self.assertEqual(401, client.get("/v1", headers=headers).status_code)
        
                # Incomplete Signature
                encoded = jwt.encode({"some": "payload"}, "asdf", algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded[1:]}"}
                self.assertEqual(401, client.get("/v1", headers=headers).status_code)
        
                # Signature
                encoded = jwt.encode({"user": self.alternative_id, "device_name": "non existent device"}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}
                self.assertEqual(404, client.get("/v1", headers=headers).status_code)

    def test_apiv1_get(self):
        with app.app_context():
            with app.test_client() as client:
                # Address not Found
                encoded = jwt.encode({"user": self.alternative_id, "device_name": "non existent device"}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}
                self.assertEqual(404, client.get("/v1", headers=headers).status_code)

                # setup device in db
                with app.app_context():
                    addr = SharedAddresses(
                        user=self.user_id,
                        device_name="TEST GET",
                        address="1.2.3.4",
                        last_updated=func.now()
                    )
                    db.session.add(addr)
                    db.session.commit()

                # Address Found
                encoded = jwt.encode({"user": self.alternative_id, "device_name": "TEST GET"}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}
                r = client.get("/v1", headers=headers)
                self.assertEqual(200, r.status_code)
                self.assertEqual("1.2.3.4", r.text)

                # clean db
                addr = SharedAddresses.query.filter_by(user=self.user_id, device_name="TEST GET").first()
                db.session.delete(addr)
                db.session.commit()

    def test_apiv1_put(self):
        with app.app_context():
            with app.test_client() as client:
                encoded = jwt.encode({"user": self.alternative_id, "device_name": "TEST PUT"}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}
                data = "1.2.3.4"

                # Create
                self.assertEqual(201, client.put("/v1", data=data, headers=headers).status_code)

                # Check
                self.assertEqual(data, client.get("/v1", headers=headers).text)

                # change again
                data = "2.3.4.5"
                self.assertEqual(200, client.put("/v1", data=data, headers=headers).status_code)

                # clean db
                addr = SharedAddresses.query.filter_by(user=self.user_id, device_name="TEST PUT").first()
                db.session.delete(addr)
                db.session.commit()

    def test_apiv1_delete(self):
        with app.app_context():
            with app.test_client() as client:
                # setup device in db
                addr = SharedAddresses(
                    user=self.user_id,
                    device_name="TEST DELETE",
                    address="1.2.3.4",
                    last_updated=func.now()
                )
                db.session.add(addr)
                db.session.commit()

                encoded = jwt.encode({"user": self.alternative_id, "device_name": "TEST DELETE"}, app.config['JWT_SECRET_KEY'], algorithm="HS256")
                headers = {"Authorization": f"Bearer {encoded}"}

                # Delete
                self.assertEqual(200, client.delete("/v1", headers=headers).status_code)

                # heck if it is deleted
                self.assertEqual(404, client.get("/v1", headers=headers).status_code)

                # deleting again should not be possible
                self.assertEqual(404, client.delete("/v1", headers=headers).status_code)
