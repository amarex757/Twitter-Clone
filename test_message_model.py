# ALL TESTS PASSED. 10/10/23 11:52pm (Ran 1 test in 0.034s)
# `python -m unittest test_message_model.py`

import os
from unittest import TestCase
from datetime import datetime
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app
db.create_all()

class UserModelTestCase(TestCase):
    # test views for messages

    def setUp(self):
        db.session.rollback()
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        user= User(
            email= "test@test.com",
            username = 'usertest',
            password = 'HASHED_PASSWORD'
        )
        db.session.add(user)
        db.session.commit()

        m = Message(
            text= "text",
            timestamp = datetime.utcnow(),
            user_id = user.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "text")
        self.assertEqual(m.user_id, user.id)