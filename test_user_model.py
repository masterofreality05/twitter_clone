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


#Does the repr method work as expected?
#Does is_following successfully detect when user1 is following user2?
#Does is_following successfully detect when user1 is not following user2?
#Does is_followed_by successfully detect when user1 is followed by user2?
#Does is_followed_by successfully detect when user1 is not followed by user2?
#Does User.create successfully create a new user given valid credentials?
#Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
#Does User.authenticate successfully return a user when given a valid username and password?
#Does User.authenticate fail to return a user when the username is invalid?
#Does User.authenticate fail to return a user when the password is invalid?

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

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

        model_test = User.query.filter(User.username == "testuser").first()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        #Does the repr method work as expected?
        self.assertIn("User #", model_test.__repr__())
        self.assertIn("test@test.com", model_test.__repr__())

    def test_user_like_message(self):
        with app.test_client() as client:
            res = client.post("/users/add_like/100")
            html = res.get_data(as_text=True)