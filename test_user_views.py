
from unittest import TestCase
from app import app, do_logout, do_login, db, g, add_user_to_g, session
from models import User

#python -m unittest test_user_views.py




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
       """test the homepage view with user logged out"""
       app.config['WTF_CSRF_ENABLED'] = False
       with app.test_client() as client:
            res = client.post("/login", data={'username':'d','password':'123456'},
            follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Hello", html)
            do_logout()
       

     #When you’re logged out, you cannot access the follower / following pages for any user?
     #When you’re logged out, are you disallowed from visiting a user’s follower / following pages?

    def test_user_following_view_loggedout(self):
        """test for the user following page when logged out"""
        with app.test_client() as client:
            app.config['WTF_CSRF_ENABLED'] = False
            user = User.query.filter(User.username == "testuser").first()
            
            print("test_user user inputted is", user)
           
            res = client.get("/users/370/following",
                             follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn("New to Warbler?", html)
            do_logout()
    
    def test_user_following_view_loggedin(self):
        """test for the user following page when logged in"""
        with app.test_client() as client:
            user = User.query.filter(User.username == "testuser").first()
            CURR_USER_KEY = "curr_user"
  
            with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = user.id
            print("test_user user inputted is", user)
            res = client.get(f"/users/{user.id}/following",
                             follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn("Following", html)
            do_logout()







