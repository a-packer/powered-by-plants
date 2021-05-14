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

