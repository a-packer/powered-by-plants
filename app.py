import os

import requests
import json
from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, Favorite
from recipe import add_structure_recipe

CURR_USER_KEY = "curr_user"


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

@app.route("/landing")
def experiment_landing_page():
    return render_template("home.html")


@app.route("/api/get-recipe")
def lucky_num_api():
    """gets recipe from spoonacular"""

    query = request.args.get("query") 
    key = "67de1636f65f4322adffda4851c70b9d"
    min_protein = request.args.get("minProtein")
    intolerances = request.args.get("intolerances")

    # import pdb; pdb.set_trace() 

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={key}&minProtein={min_protein}&intolerances=gluten&number=3&diet=vegan&query={query}&addRecipeInformation=True") 
    response_string = res.text
    response_dict = json.loads(response_string) #convert to json dict

    # import pdb; pdb.set_trace() 

    results = response_dict['results'] #get results as list
 

    if results: #if there is at least one recipe returned
        recipe = results[0]  #gets results for first recipe from search query(current limit 3 recipes) then parses through response to get to protien amount
        nutrition = recipe["nutrition"]  
        nutrients = nutrition["nutrients"]
        protein = nutrients[0]
        amount = protein["amount"]  


        return jsonify(response_dict) 
    
    else:
        return jsonify({'results': [{'error' : 'none'}]})

   


@app.route("/recipe/<int:recipe_id>", methods=["POST"])
def add_recipe(recipe_id):
    """Adds recipe to db"""

    res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")

    # import pdb; pdb.set_trace() 
    recipe = add_structure_recipe(res) #adds recipe to db, then returns relevant and structured recipe information

    return redirect(f"/recipe/{recipe.id}")

@app.route('/recipe/<int:recipe_id>', methods=["GET"])
def messages_show(recipe_id):
    """show recipe ingredients, instructions"""

    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = json.loads(recipe.ingredients)  #convert from json to list
    optional_ing = [ing for ing in ingredients if ing[1] == 'servings']
    instructions = json.loads(recipe.instructions) #convert from json to list
    # import pdb; pdb.set_trace() 
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, optional_ing=optional_ing, instructions=instructions)







##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged Out", 'danger')

    return redirect('/')


##############################################################################
# General user routes:


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile and favorite recipes"""

    user = User.query.get_or_404(user_id)

    # TODO: get favorites
    # favorites = (Favorite
    #             .query
    #             .filter(Favorite.user_id == user_id)
    #             .limit(10)
    #             .all())
    # TODO: make user.html template
    return render_template('user.html', user=user, favorites=favorites)
    

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


@app.route('/users/add_fav/<int:recipe_id>', methods=["GET", "POST"])
def add_like(recipe_id):
    """Add favorite recipe"""

    user = User.query.get_or_404(g.user.id)
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # check to see if recipe in liked favorite recipes already. If not, add to recipes
    fav_recipes = user.recipes

    # import pdb; pdb.set_trace()
   
    fav_recipe_ids = [fav_recipe.id for fav_recipe in fav_recipes]
    if recipe.id in fav_recipe_ids:
        fav_recipe_ids.remove(recipe.id)
        user.recipes = [Recipe.query.get(recipe_id) for recipe_id in fav_recipe_ids]
        db.session.commit()
        # return (f"recipe {recipe.title} removed from {user.first_name}'s favorites")
        return redirect('/recipe/<int:recipe_id>')
    else:
        user.recipes.append(Favorite(user_id=user.id, recipe_id=recipe_id)) 
        db.session.commit()
        # return (f"recipe {recipe.title} added to {user.first_name}'s favorites")
        return redirect('/recipe/<int:recipe_id>')
   
   

