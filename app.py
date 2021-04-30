import os

from flask import Flask, render_template, request, jsonify
import requests
import json
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


# from forms import UserAddForm, LoginForm
from models import db, connect_db, User


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///vegan_users'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")

@app.route("/api/get-recipe")
def lucky_num_api():
    """gets recipe from spoonacular"""

    query = request.args.get("query")
    # Todo: get user input for recipe search: minProtien and intolerances

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey=67de1636f65f4322adffda4851c70b9d&minProtein=20&intolerances=gluten&number=3&diet=vegan&query={query}") 
    # res = requests.get(f"http://numbersapi.com/{lucky_num}")
    response_string = res.text
    response_dict = json.loads(response_string) #convert to json dict

    # import pdb; pdb.set_trace() 

    return jsonify(response_dict)  