# ALL TESTS PASSED 10/10/23 12:12am (Ran 7 tests in 1.768s)
# `FLASK_ENV=production python -m unittest test_message_views.py`

import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_follower_following_pages_logged_in(self):
        """Test if follower/following pages are accessible when logged in."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Make a request to the follower page
            resp = c.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)

            # Make a request to the following page
            resp = c.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(resp.status_code, 200)
    
    def test_follower_following_pages_logged_out(self):
        """Test if follower/following pages are disallowed when logged out."""

        with self.client as c:
            # Make a request to the follower page
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Followers", resp.get_data(as_text=True))

            # Make a request to the following page
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Following", resp.get_data(as_text=True))
    
    def test_add_message_logged_in(self):
        """Test if a message can be added when logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertEqual(msg.user_id, self.testuser.id)
    
    def test_delete_message_logged_in(self):
        """Test if a message can be deleted when logged in."""

        # Create a message by the test user
        message = Message(
            text="Test message",
            user_id=self.testuser.id
        )
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            # Check if the message is deleted from the database
            msg = Message.query.get(message.id)
            self.assertIsNone(msg)
    
    def test_add_message_logged_out(self):
        """Test if adding a message is prohibited when logged out."""
        
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Hello", resp.get_data(as_text=True))
    
    def test_delete_message_logged_out(self):
        """Test if deleting a message is prohibited when logged out."""

        # Create a message by the test user
        message = Message(
            text="Test message",
            user_id=self.testuser.id
        )
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # Check if the message still exists in the database
            msg = Message.query.get(message.id)
            self.assertEqual(msg, message)