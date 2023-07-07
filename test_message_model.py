from unittest import TestCase
from app import db, User, Message, app

#python -m unittest test_message_model.py

class TestMessageModel(TestCase):
    """test the model for our messages"""

    def setUp(self):
        """do this before each test"""
     
        Message.query.delete()
       

    
    def tearDown(self):
        """do this after each test"""
        db.session.rollback()

    def test_message_model(self):
        """a test for the various attributes on our message class instances"""
        CURR_USER_KEY = "jim"
        user = User.query.filter(User.username == "testuser").first()
        message = Message(text="testmessagetext",user_id=user.id)
        db.session.add(message)
        db.session.commit()
        found_message = Message.query.filter(Message.text == "testmessagetext").first()
        print(found_message.text)
        self.assertEqual(found_message.text, "testmessagetext")
        self.assertEqual(found_message.user_id, user.id)


        
      