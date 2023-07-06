from unittest import TestCase
from app import app, do_logout, db

#python -m unittest test_user_model.py


class TestHomepageViews(TestCase):
    """unit tests to measure our sql interaction with crud"""

    def setUp(self):
        """clean up any existing rows in our table"""

    def tearDown(self):
        """clean up any fouled transaction with rollback"""
        db.session.rollback()

    def test_homepage_logged_out(self):
        """test the homepage view with no user logged in"""
        with app.test_client() as client:
            res = client.get("/")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Sign up now to get your own personalized timeline!", html)
    
    def test_homepage_logged_in(self):
       """test the homepage view with no user logged in"""
       app.config['WTF_CSRF_ENABLED'] = False
       with app.test_client() as client:
            res = client.post("/login", data={'username':'damo','password':'ghbghb'},
            follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Hello", html)
            do_logout()
       


