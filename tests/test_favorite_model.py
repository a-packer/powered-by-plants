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

        self.assertEqual(str(u), f'<User #{u.id}: {u.first_name} {u.last_name}, {u.username}, {u.email}>')


    

    
 
