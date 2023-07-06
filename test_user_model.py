"""User model tests."""

# run these tests like:
#
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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        follow_u = User(
            email="followtest@test.com",
            username="followtestuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        db.session.add(follow_u)
        db.session.commit()

        self.client = app.test_client()

        

    def test_user_model(self):
        """Does basic model work?"""
        u = User.query.filter(User.username == "testuser").first()

      
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_isfollowed_by(self):
        """does the class method isfolllowed by work?"""
        u = User.query.filter(User.username == "testuser").first()
        follow_u = User.query.filter(User.username == "followtestuser").first()
        print("---------u id", u.id, "------------follower id", follow_u.id)

        following = Follows(user_being_followed_id=u.id, user_following_id=follow_u.id)
        db.session.add(following)
        db.session.commit()
        follow_info = Follows.query.filter(Follows.user_being_followed_id == u.id).first()
        print("heres our follow info", follow_info)

        self.assertEqual(True, u.is_followed_by(follow_u))

