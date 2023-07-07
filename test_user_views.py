
from unittest import TestCase
from app import app, do_logout, db
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
            res = client.get("/users/370/following",
                             follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn("New to Warbler?", html)
            do_logout()
    
    #When you’re logged in, you can access the follower / following pages for any user?
    
    def test_user_following_view_loggedin(self):
        """test for the user following page when logged in"""
        with app.test_client() as client:
            user = User.query.filter(User.username == "testuser").first()
            CURR_USER_KEY = "curr_user"

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        #we have first established our app.testclient as client. 
        #within that we can access the session of our test client with the session_transaction method called on client
        #we then define that as sess for later use
        #here we can attribute "sess" with CURR_USER_KEY which we obtain from the id property on our user variable
        #just to recap our user variable is an class instance stored in our db queried via SQL by its username of "testuser"
        #now that we have stored a current user in sess aka client.session_transaction() we can mimic logging in
        #therefore now the view testing is ready to test if we return the correct html markup from our get request

            with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = user.id
            res = client.get(f"/users/{user.id}/following",
                             follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn("Following", html)
            do_logout()







