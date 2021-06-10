"""Recipe model tests."""

# run these tests in terminal like:
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Recipe


os.environ['DATABASE_URL'] = "postgresql:///powered_by_plants_test"
from app import app

# Create our tables once for all tests --- 
# in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class RecipeModelTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""

        Recipe.query.delete()

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_recipe_model(self):
        """Does recipe model work?"""

        r = Recipe(
            id = 1111111111, 
            title = "Yum Yum Food",
            img = "google.com",
            protein = 13,
            source_url = "google.com",
            ingredients = ["chocolate", "strawberries"],
            instructions = ["mix", "stir"],
            time = 10,
            servings = 2 
        )

        db.session.add(r)
        db.session.commit()

        # Recipe is not favorited by any users
        self.assertEqual(len(r.users), 0)

        self.assertEqual(str(r), f'<Recipe #{r.id}: {r.title}, {r.img}, {r.protein}>')