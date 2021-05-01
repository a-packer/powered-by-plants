import os

from flask import Flask, render_template, request, jsonify
import requests
import json
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

# TODO: add user signup and login forms
# from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, Favorite


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///powered_by_plants'))

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
    key = "67de1636f65f4322adffda4851c70b9d"
    intolerances = request.args.get("intolerances")
    # Todo: get user input for recipe search: minProtien and intolerances


    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={key}&minProtein=15&intolerances={intolerances}&number=3&diet=vegan&query={query}&addRecipeInformation=True") 
    response_string = res.text
    response_dict = json.loads(response_string) #convert to json dict


    results = response_dict['results'] #get results as list

    recipe = results[0]  #gets results for first recipe from search query(current limit 3 recipes) then parses through response to get to protien amount
    nutrition = recipe["nutrition"]  
    nutrients = nutrition["nutrients"]
    protein = nutrients[0]
    amount = protein["amount"]


    # import pdb; pdb.set_trace() 

    return jsonify(response_dict)  


@app.route("/recipe", methods=["GET"])
def show_recipe_details():
    """show recipe ingredients, instructions"""

    return render_template('recipe.html')


@app.route("/recipe", methods=["POST"])
def add_recipe():
    """Adds recipe to db"""

    # TODO: pass in recipe results and add to db

        # recipe = Recipe.addRecipe(
        #     title= ,
        #     img= ,
        #     protien= ,
        #     api_url= ,
        #     source_url= ,
        #     instructions= ,
        # )

        # db.session.commit()