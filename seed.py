"""Seed file to make sample data for db."""

from models import User, Recipe, Favorite, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

User.query.delete()

# Add sample users 
ann = User(first_name='Ann', last_name="Hathaway", email="ann@email.com", username="annway", password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe")
donald = User(first_name='Donald', last_name="Duck", email="donald@email.com", username="dDog", password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe")
marco = User(first_name='Marco', last_name="Polo", email="marco@email.com", username="MarcoP", password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe")
sandra = User(first_name='Sandra', last_name="Dee", email="sdee@email.com", username="sandy", password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe")

db.session.add_all([ann, donald, marco, sandra])
db.session.commit()

# Add sample recipes
# quinoa = Recipe(title="Quinoa Salad", img="quinoa.jpg", protein=15)
# pbj = Recipe(title="Peanut Butter and Jelly Sandwich", protein= 10)
# kidneybean = Recipe(title="Kidney Bean Salad", img="www.beansalad.jpg", protein=25)
# coffee = Recipe(title="Coffee Protein Shake", img="www.coffe.jpg", protein=12)
# tempeh = Recipe(title="Tempeh Tacos", img="www.taco.jpg", protein=24)
# quinoasoup = Recipe(title="Quinoa Mexi Soup", img="www.soup.jpg", protein=30)
# tofu = Recipe(title="Tofu Wraps", img="www.tofu.jpg", protein=22)


# db.session.add_all([quinoa, pbj, kidneybean, coffee, tempeh, quinoasoup, tofu])
# db.session.commit()


