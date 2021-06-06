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

@app.route("/cuisine")
def cuisine_search_results():
    return render_template("cuisine.html")

@app.route("/popular")
def popular_search_results():
    return render_template("popular.html")

@app.route("/search")
def search_page():
    return render_template('search.html')


@app.route("/api/get-recipes")
def gets_recipes_from_spoonacular():
    """gets recipe from spoonacular"""

    query = request.args.get("query") 
    key = "67de1636f65f4322adffda4851c70b9d"
    min_protein = request.args.get("minProtein")
    intolerances = request.args.get("intolerances")

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={key}&minProtein={min_protein}&intolerances={intolerances}&number=3&diet=vegan&query={query}&addRecipeInformation=True") 
    response_string = res.text
    response_dict = json.loads(response_string) #convert to json dict

    results = response_dict['results'] #get results as list 
    
    if results: # if there is at least one recipe returned
        for i in range(len(results)): # loop through the recipes to check to see if in db. if not, add to db

            recipe = results[i]  # gets results for recipe
            recipe_id = recipe['id']

            db_recipe = Recipe.query.filter_by(id=recipe_id).first() 
            if db_recipe == None:  # if no recipe is returned, get recipe data from api by id, then add recipe to db
                res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")
                recipe = add_structure_recipe(res) # adds recipe to db, then returns relevant and structured recipe information
    
        return jsonify(response_dict) 
    
    else: # if the search gives no results

        import pdb; pdb.set_trace() 

        return jsonify({'results': [{'error' : 'none'}]})

   

@app.route("/recipe/<int:recipe_id>", methods=["POST"])
def add_recipe(recipe_id):
    """Adds recipe to db"""
    import pdb; pdb.set_trace() 

    res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")

    import pdb; pdb.set_trace() 
    recipe = add_structure_recipe(res) #adds recipe to db, then returns relevant and structured recipe information

    return redirect(f"/recipe/{recipe.id}")



@app.route('/recipe/<int:recipe_id>', methods=["GET"])
def messages_show(recipe_id):
    """show recipe ingredients, instructions"""

    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = json.loads(recipe.ingredients)  #convert from json to list
    optional_ing = [ing for ing in ingredients if ing[1] == 'servings']
    instructions = json.loads(recipe.instructions) #convert from json to list

        
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

    favorites = Favorite.query.filter(Favorite.user_id == user_id).limit(10).all()

    fav_recipes = [Recipe.query.get_or_404(favorite.recipe_id) for favorite in favorites]
    

    return render_template('user.html', user=user, favorites=favorites, fav_recipes=fav_recipes)
    

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



#################
# Favorites

@app.route('/users/add_fav/<int:recipe_id>', methods=["GET", "POST"])
def add_like(recipe_id):
    """Add favorite recipe"""  

    user = User.query.get_or_404(g.user.id)
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # check to see if recipe in favorite recipes already. If already a favorite, remove from favorite recipes. If not, add to favorite recipes. 
    fav_recipes = user.recipes 
    fav_recipe_ids = [fav_recipe.recipe_id for fav_recipe in fav_recipes]

    if recipe.id in fav_recipe_ids:
        updated_fav_recipes = [] # TODO: There must be a way to remove from favorites without remaking a favorites list and just not adding the one that's being removed
        for favorite in fav_recipes:
            if recipe.id == favorite.recipe_id:
                pass
            else:
                updated_fav_recipes.append(favorite)
        
        user.recipes = updated_fav_recipes
        db.session.commit()

        flash(f"Removed {recipe.title} from favorites", "danger")
        return redirect(f"/recipe/{recipe.id}")

    else:
        g.user.recipes.append(Favorite(user_id=user.id, recipe_id=recipe_id)) 
        db.session.commit()

        flash(f"Added {recipe.title} to favorites", "success")
        return redirect(f"/recipe/{recipe.id}")
   
   

