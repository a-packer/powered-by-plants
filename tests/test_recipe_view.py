"""Recipe View Tests"""

# run these tests like:
#    FLASK_ENV=production python -m unittest test_recipe_views.py


import os
from unittest import TestCase

from models import db, connect_db, Recipe, User, Favorite


os.environ['DATABASE_URL'] = "postgresql:///powered_by_plants_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class RecipeViewTestCase(TestCase):
    """Test views for recipes."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Recipe.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_recipe(self):
        """Can use add a recipe?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                # sess[CURR_USER_KEY] = self.testuser.id

                resp = c.post("/recipes/new", data={"text": "Hello"})

                # Make sure it redirects
                self.assertEqual(resp.status_code, 302)

                msg = Recipe.query.one()
                self.assertEqual(msg.text, "Hello")

    # def test_add_recipe_no_curr_user(self):
    #     with self.client as c:
    #         resp = c.post("/recipes/new", data={"text": "Hello"}, follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized.", str(resp.data))

    # def test_add_recipe_with_invalid_user(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = 99999999999999999999 #not a valid user_id
    #         resp = c.post("/recipes/new", data={"text": "Hello"}, follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    # def test_invalid_recipe_show(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id        
    #         resp = c.get('/recipes/99999999')
    #         self.assertEqual(resp.status_code, 404)
    
    # def test_valid_recipe_deletion(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id 
    #         u = User.signup(username="testuser_valid_recipe", email="testemail@email.com", password="testpassword", image_url=None)
    #         db.session.add(u)
    #         db.session.commit()
    #         u_id = u.id

    #         m = Recipe(text="I must be deleted", user_id=u_id) 
    #         db.session.add(m)
    #         db.session.commit()

    #         m_id = m.id
    #         resp = c.post(f'/recipes/{m.id}/delete', follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    # def test_invalid_recipe_deletion(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id 

    #         resp = c.post(f'/recipes/999999999999999999/delete', follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized.", str(resp.data))



            



