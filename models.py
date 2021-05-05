"""SQLAlchemy models for Powered By Plants."""

from datetime import datetime
import bcrypt

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)




class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text,nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<User #{self.id}: {self.first_name} {self.last_name}, {self.username}, {self.email}>"

    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first() 

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False




class Recipe(db.Model):
    """Vegan recipe accessed by user and saved in db"""

    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    img = db.Column(db.Text)
    protein = db.Column(db.Integer, nullable=False)
    api_id = db.Column(db.Integer, nullable=False, unique=True) #api_id needs to be unique! keep out duplicates
    source_url = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    time = db.Column(db.Text)
    servings = db.Column(db.Text)
    
    def __repr__(self):
        return f"<Recipe #{self.id}: {self.title}, {self.img}, {self.protein}>"

    @classmethod
    def addRecipe(cls, title, img, protein, api_id, source_url, ingredients, instructions, time, servings):
        """Adds a recipe to the db"""

        recipe = Recipe(
            title=title,
            img=img,
            protein=protein,
            api_id=api_id,
            source_url=source_url,
            ingredients=ingredients,
            instructions=instructions,
            time=time,
            servings=servings
        )

        db.session.add(recipe)
        return recipe




class Favorite(db.Model):
    """Recipes favorited by Users"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete="CASCADE"))

    user = db.relationship("User", backref="recipes")
    recipe = db.relationship("Recipe", backref="users")

    

