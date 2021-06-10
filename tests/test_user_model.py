"""User model tests."""

# run these tests in terminal like:
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Recipe, Favorite


os.environ['DATABASE_URL'] = "postgresql:///powered_by_plants_test"
from app import app

# Create our tables once for all tests --- 
# in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        Favorite.query.delete()
        Recipe.query.delete()

        self.client = app.test_client()

        u1 = User.signup("Bob", "Jones", "user1", "user1@email.com", "password1")
        u1_id = 1111
        u1.id = u1_id 

        u2 = User.signup("Cher", "Hart", "user2", "user2@email.com", "password2")
        u2_id = 2222
        u2.id = u2_id 

        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.u1_id = u1_id

        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name="Michelle",
            last_name="Bower",
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no favorited recipes
        self.assertEqual(len(u.recipes), 0)

        self.assertEqual(str(u), f'<User #{u.id}: {u.first_name} {u.last_name}, {u.username}, {u.email}>')


    # SIGN UP / SIGN IN TESTS

    def test_valid_signup(self):
        u_test = User.signup("signinuser", "userlast", "signedin", "signintest@email.com", "password3")
        uid = 3333
        u_test.id = uid
        db.session.commit()

        user_test = User.query.get_or_404(uid)

        self.assertEqual(user_test.first_name, "signinuser")
        self.assertEqual(user_test.last_name, "userlast")
        self.assertEqual(user_test.email, "signintest@email.com")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_signup(self):
        invalid = User.signup(None, "last", "invaliduser", "test@test.com", "password")
        uid = 4444
        invalid.id = uid
        # if data missing, Integrity Error will appear after db.session.commit()
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_sign_in(self):
        u = User.authenticate(self.u1.username, "password1")
        self.assertIsNotNone(u)

    def test_invalid_password(self):
        u = User.authenticate(self.u1.username, "badpassword")
        self.assertFalse(u)

    def test_invalid_password(self):
        u = User.authenticate("wrong username", "password1")
        self.assertFalse(u)


    
 
