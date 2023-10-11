# ALL TESTS PASSED 10/10/23 12:12am (Ran 7 tests in 2.618s)
# run these tests like:
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
# db.create_all()
class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        db.drop_all()
        db.create_all()        

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        
        u = User(
            email = "test@testmail.com",
            username = "testuser",
            password = "HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        expected = f"<User #{u.id}: {u.username}, {u.email}>"
        actual = u.__repr__()

        self.assertEqual(actual, expected)
    
    def test_is_following(self):

        u1 = User(username="user1", email="user1@example.com", password="!047password")
        u2 = User(username="user2", email="user2@example.com", password="?932password")
        db.session.add_all([u1, u2])
        db.session.commit()

        is_following = u1.is_following(u2)
        self.assertFalse(is_following)

        u1.following.append(u2)
        db.session.commit()

        is_following = u1.is_following(u2)
        self.assertTrue(is_following)

    def test_is_followed_by(self):

        u1 = User(username="user1", email="user1@example.com", password="!047password")
        u2 = User(username="user2", email="user2@example.com", password="?932password")
        db.session.add_all([u1, u2])
        db.session.commit()

        is_followed_by = u1.is_followed_by(u2)
        self.assertFalse(is_followed_by)

        u2.following.append(u1)
        db.session.commit()

        is_followed_by = u1.is_followed_by(u2)
        self.assertTrue(is_followed_by)

    def test_create_new_user(self):
        user = User.signup(username="testuser", email="test@test.com", password="password", image_url=None)

        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@test.com")

    def test_create_new_user_invalid_creds(self):
        user = User.signup(username="test-user", email="test-user@test.com", password="test-password", image_url=None)
        db.session.add(user)
        db.session.commit()

        with self.assertRaises(Exception):
            user = User.signup(username="test-user2", email="test-user@test.com", password="test-password2", image_url=None)
            db.session.add(user)
            db.session.commit()  
        # missing username      
        with self.assertRaises(Exception):
            user = User.signup(username=None, email="test-user2@test.com", password="test-password3", image_url=None)
            db.session.add(user)
            db.session.commit()    
        # missing password
        with self.assertRaises(Exception):
            user = User.signup(username="test-user3", email="test3@test.com", password=None, image_url=None)
            db.session.add(user)
            db.session.commit() 
        # missing email       
        with self.assertRaises(Exception):
            user = User.signup(username="test-user4", email=None, password='password', image_url=None)
            db.session.add(user)
            db.session.commit()

    def test_authenticate(self):
        # create user with valid credentials
        u = User.signup(username="test-user", email="test@test.com", password="password", image_url=None)
        u2 = User.signup(username="test_user", email="test_@test.com", password="password!", image_url=None)
        db.session.commit()
        # attempt to authenticate with valid credentials 
        auth_user = User.authenticate(username="test-user", password="password")
        # assert authenticated user is the same as original user
        self.assertEqual(auth_user, u)
        # attempt to authenticate with valid credentials username
        auth_user = User.authenticate(username="test_user", password="password!")
        self.assertEqual(auth_user, u2)
        # attempt to authenticate with invalid username
        auth_user = User.authenticate(username="invalidusername", password="password")
        # assert authenticated user is None
        self.assertFalse(auth_user)
        # attempt to authenticate with invalid password
        auth_user = User.authenticate(username="test-user", password="invalidpassword")
        # assert authenticated user is None
        self.assertFalse(auth_user)

        auth_user = User.authenticate(username="user", password="hiddensecret")
        self.assertFalse(auth_user)
        auth_user = User.authenticate(username="test", password="testpass")
        self.assertFalse(auth_user)



