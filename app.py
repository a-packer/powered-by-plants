import os
from pdb import set_trace

import requests
import json
from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError



from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, Favorite
from login_logout import do_login, do_logout
from recipe import add_structure_recipe, gets_recipes

CURR_USER_KEY = "curr_user"


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///powered_by_plants'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

API_KEY = "67de1636f65f4322adffda4851c70b9d"


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")

##############################################################################
# Recipe Search/filtering routes 

@app.route("/search")
def search_page():
    return render_template('recipe_templates/search.html')

@app.route("/cuisine")
def cuisine_search():
    """landing page for recipe cuisines to search by"""
    return render_template("recipe_templates/cuisine.html")

@app.route("/cuisine/<cuisine>")
def cuisine_search_results(cuisine):
    """Gets recipes for a specified cuisine"""

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&minProtein=5&number=8&diet=vegan&addRecipeInformation=True&cuisine={cuisine}") 
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
    
        cuisine_recipes = []
        for recipe in response_dict["results"]:
            recipe = Recipe.query.get_or_404(recipe["id"])
            cuisine_recipes.append(recipe)
    
    else: # if the search gives no results
        return redirect('/cuisine')
    
    return render_template("recipe_templates/cuisine_recipes.html", cuisine_recipes=cuisine_recipes)

@app.route("/popular")
def popular_search_results():
    """Returns recipes favorited by users"""
    
    favorites = Favorite.query.all()
    fav_ids = [favorite.recipe_id for favorite in favorites]
    fav_ids_set = set(fav_ids) #remove duplicates

    top_recipes = []
    for id in fav_ids_set:
        top_recipes.append(Recipe.query.get_or_404(id))
    
    return render_template("recipe_templates/popular.html", top_recipes=top_recipes)

@app.route("/api/get-recipes")
def gets_recipes_from_spoonacular():
    """gets recipe from spoonacular and returns recipe json data. If recipe not in db, add recipe to db."""

    query = request.args.get("query") 
    min_protein = request.args.get("minProtein")
    intolerances = request.args.get("intolerances")

    response_dict = gets_recipes(API_KEY, min_protein, intolerances, query) # make request to API with query data
    results = response_dict['results'] # get recipe results as list

    
    if len(results) > 0: # if there is at least one recipe returned
        for i in range(len(results)): # loop through the recipes to check to see if in db. if not, add to db

            recipe_info = results[i]  # get info for recipe, including the recipe id
            recipe_id = recipe_info['id']

            db_recipe = Recipe.query.filter_by(id=recipe_id).first() # check db to see if it contains a recipe with the id in question
            if db_recipe == None:  # if no recipe is returned, get recipe data from api by the id, then add recipe to db
                res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")
                add_structure_recipe(res) # adds recipe to db, then returns relevant and structured recipe information
    
        return jsonify(response_dict) 
    
    else: # if the search gives no results

        return redirect('/search')


   
@app.route('/recipe/<int:recipe_id>', methods=["GET"])
def messages_show(recipe_id):
    """show recipe ingredients, instructions"""

    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = json.loads(recipe.ingredients)  # convert from json to list
    for ing in ingredients:
        ing[0] = round(ing[0], 2) # round the ingredient amount
    optional_ing = [ing for ing in ingredients if ing[1] == 'servings']
    print(ingredients)
    instructions = json.loads(recipe.instructions) # convert from json to list
 
    # determine if recipe is current user's favorite
    recipe_favorites = recipe.users
    user_ids = [favorite.user_id for favorite in recipe_favorites]
    user_ids_set = set(user_ids)
    user_ids_unique = [id for id in user_ids_set]
    
    try:
        g.user.id
    except AttributeError:
        user_favorite = False
    else:        
        if g.user.id in user_ids_unique:
            user_favorite = True
        else:
            user_favorite = False
        
    return render_template('recipe_templates/recipe.html', recipe=recipe, ingredients=ingredients, optional_ing=optional_ing, instructions=instructions, user_favorite=user_favorite)



##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. 
    If the there already is a user with that username: flash message
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
            return render_template('user_templates/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('user_templates/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('user_templates/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged Out", 'danger')

    return redirect('/')


####################################################################
# General user routes:


@app.route('/user/<int:user_id>')
def users_show(user_id):
    """Show user profile and favorite recipes"""

    if not g.user:
        flash("Login/Signup To See Favorited Recipes.", "danger")
        return redirect("/login")

    user = User.query.get_or_404(user_id)

    favorites = Favorite.query.filter(Favorite.user_id == user_id).limit(10).all()

    fav_recipes = [Recipe.query.get_or_404(favorite.recipe_id) for favorite in favorites]
    

    return render_template('user_templates/user.html', user=user, favorites=favorites, fav_recipes=fav_recipes)
    

@app.route('/user/delete/<int:user_id>', methods=["GET"]) # check user's credentials. If user is attempting to delete their own account, redirect to delete_check page
def delete_user_check(user_id):
    """First step to deleting a user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(f"/user/{user_id}")

    if g.user.id != user_id:
        import pdb; pdb.set_trace()
        flash("Unauthorized. Need to be signed in as this user.", "danger")
        return redirect(f"/user/{user_id}")
    else:
        return render_template("user_templates/delete_check.html")

    
@app.route('/user/delete/<int:user_id>', methods=["POST"])
def delete_user(user_id):
    """Deletes user from database."""

    if g.user.id == user_id:
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

    flash(f"Profile Deleted", "danger")
    return redirect("/signup")
     


######################################################################
# Favorites

@app.route('/user/favorite/<int:recipe_id>', methods=["GET", "POST"])
def favorite_recipe(recipe_id):
    """Add or remove favorite recipe"""  

    if not g.user:
        flash("Login/Signup To Save Recipes.", "danger")
        return redirect(f"/recipe/{recipe_id}")

    user = User.query.get_or_404(g.user.id)
    recipe = Recipe.query.get_or_404(recipe_id)
    fav_recipes = Favorite.query.filter_by(user_id=user.id).all()
    
    # check to see if recipe in favorite recipes already. If already a favorite, remove from favorite recipes. If not, add to favorite recipes. 
    fav_recipe_ids = [fav_recipe.recipe_id for fav_recipe in fav_recipes]
  
    if recipe.id in fav_recipe_ids: # If this recipe id is already in current user's favorites, delete it

        for fav in fav_recipes: # loop through user's favorite recipes
            if recipe.id == fav.recipe_id:  # when it gets to the recipe we are trying to delete
                f = Favorite.query.get(fav.id)  # get the Favorite object that relates this user this recipe by the Favorite's id
                db.session.delete(f)
                db.session.commit()
            else:
                pass
        
        flash(f"Removed {recipe.title} from favorites", "danger")
        return redirect(f"/recipe/{recipe.id}")

    else:
        g.user.recipes.append(Favorite(user_id=user.id, recipe_id=recipe_id)) 
        db.session.commit()

        flash(f"Added {recipe.title} to favorites", "success")
        return redirect(f"/recipe/{recipe.id}")
   
   

=======
import os
from pdb import set_trace

import requests
import json
from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError



from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, Favorite
from login_logout import do_login, do_logout
from recipe import add_structure_recipe, gets_recipes

CURR_USER_KEY = "curr_user"


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///powered_by_plants'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

API_KEY = "67de1636f65f4322adffda4851c70b9d"


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("index.html")

##############################################################################
# Recipe Search/filtering routes 

@app.route("/search")
def search_page():
    return render_template('recipe_templates/search.html')

@app.route("/cuisine")
def cuisine_search():
    """landing page for recipe cuisines to search by"""
    return render_template("recipe_templates/cuisine.html")

@app.route("/cuisine/<cuisine>")
def cuisine_search_results(cuisine):
    """Gets recipes for a specified cuisine"""

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&minProtein=5&number=8&diet=vegan&addRecipeInformation=True&cuisine={cuisine}") 
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
    
        cuisine_recipes = []
        for recipe in response_dict["results"]:
            recipe = Recipe.query.get_or_404(recipe["id"])
            cuisine_recipes.append(recipe)
    
    else: # if the search gives no results
        return redirect('/cuisine')
    
    return render_template("recipe_templates/cuisine_recipes.html", cuisine_recipes=cuisine_recipes)

@app.route("/popular")
def popular_search_results():
    """Returns recipes favorited by users"""
    
    favorites = Favorite.query.all()
    fav_ids = [favorite.recipe_id for favorite in favorites]
    fav_ids_set = set(fav_ids) #remove duplicates

    top_recipes = []
    for id in fav_ids_set:
        top_recipes.append(Recipe.query.get_or_404(id))
    
    return render_template("recipe_templates/popular.html", top_recipes=top_recipes)

@app.route("/api/get-recipes")
def gets_recipes_from_spoonacular():
    """gets recipe from spoonacular and returns recipe json data. If recipe not in db, add recipe to db."""

    query = request.args.get("query") 
    min_protein = request.args.get("minProtein")
    intolerances = request.args.get("intolerances")

    response_dict = gets_recipes(API_KEY, min_protein, intolerances, query) # make request to API with query data
    results = response_dict['results'] # get recipe results as list

    
    if len(results) > 0: # if there is at least one recipe returned
        for i in range(len(results)): # loop through the recipes to check to see if in db. if not, add to db

            recipe_info = results[i]  # get info for recipe, including the recipe id
            recipe_id = recipe_info['id']

            db_recipe = Recipe.query.filter_by(id=recipe_id).first() # check db to see if it contains a recipe with the id in question
            if db_recipe == None:  # if no recipe is returned, get recipe data from api by the id, then add recipe to db
                res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")
                add_structure_recipe(res) # adds recipe to db, then returns relevant and structured recipe information
    
        return jsonify(response_dict) 
    
    else: # if the search gives no results

        return redirect('/search')


   
@app.route('/recipe/<int:recipe_id>', methods=["GET"])
def messages_show(recipe_id):
    """show recipe ingredients, instructions"""

    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = json.loads(recipe.ingredients)  # convert from json to list
    for ing in ingredients:
        ing[0] = round(ing[0], 2) # round the ingredient amount
    optional_ing = [ing for ing in ingredients if ing[1] == 'servings']
    print(ingredients)
    instructions = json.loads(recipe.instructions) # convert from json to list
 
    # determine if recipe is current user's favorite
    recipe_favorites = recipe.users
    user_ids = [favorite.user_id for favorite in recipe_favorites]
    user_ids_set = set(user_ids)
    user_ids_unique = [id for id in user_ids_set]
    
    try:
        g.user.id
    except AttributeError:
        user_favorite = False
    else:        
        if g.user.id in user_ids_unique:
            user_favorite = True
        else:
            user_favorite = False
        
    return render_template('recipe_templates/recipe.html', recipe=recipe, ingredients=ingredients, optional_ing=optional_ing, instructions=instructions, user_favorite=user_favorite)



##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. 
    If the there already is a user with that username: flash message
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
            return render_template('user_templates/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('user_templates/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('user_templates/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged Out", 'danger')

    return redirect('/')


####################################################################
# General user routes:


@app.route('/user/<int:user_id>')
def users_show(user_id):
    """Show user profile and favorite recipes"""

    if not g.user:
        flash("Login/Signup To See Favorited Recipes.", "danger")
        return redirect("/login")

    user = User.query.get_or_404(user_id)

    favorites = Favorite.query.filter(Favorite.user_id == user_id).limit(10).all()

    fav_recipes = [Recipe.query.get_or_404(favorite.recipe_id) for favorite in favorites]
    

    return render_template('user_templates/user.html', user=user, favorites=favorites, fav_recipes=fav_recipes)
    

@app.route('/user/delete/<int:user_id>', methods=["GET"]) # check user's credentials. If user is attempting to delete their own account, redirect to delete_check page
def delete_user_check(user_id):
    """First step to deleting a user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(f"/user/{user_id}")

    if g.user.id != user_id:
        import pdb; pdb.set_trace()
        flash("Unauthorized. Need to be signed in as this user.", "danger")
        return redirect(f"/user/{user_id}")
    else:
        return render_template("user_templates/delete_check.html")

    
@app.route('/user/delete/<int:user_id>', methods=["POST"])
def delete_user(user_id):
    """Deletes user from database."""

    if g.user.id == user_id:
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

    flash(f"Profile Deleted", "danger")
    return redirect("/signup")
     


######################################################################
# Favorites

@app.route('/user/favorite/<int:recipe_id>', methods=["GET", "POST"])
def favorite_recipe(recipe_id):
    """Add or remove favorite recipe"""  

    if not g.user:
        flash("Login/Signup To Save Recipes.", "danger")
        return redirect(f"/recipe/{recipe_id}")

    user = User.query.get_or_404(g.user.id)
    recipe = Recipe.query.get_or_404(recipe_id)
    fav_recipes = Favorite.query.filter_by(user_id=user.id).all()
    
    # check to see if recipe in favorite recipes already. If already a favorite, remove from favorite recipes. If not, add to favorite recipes. 
    fav_recipe_ids = [fav_recipe.recipe_id for fav_recipe in fav_recipes]
  
    if recipe.id in fav_recipe_ids: # If this recipe id is already in current user's favorites, delete it

        for fav in fav_recipes: # loop through user's favorite recipes
            if recipe.id == fav.recipe_id:  # when it gets to the recipe we are trying to delete
                f = Favorite.query.get(fav.id)  # get the Favorite object that relates this user this recipe by the Favorite's id
                db.session.delete(f)
                db.session.commit()
            else:
                pass
        
        flash(f"Removed {recipe.title} from favorites", "danger")
        return redirect(f"/recipe/{recipe.id}")

    else:
        g.user.recipes.append(Favorite(user_id=user.id, recipe_id=recipe_id)) 
        db.session.commit()

        flash(f"Added {recipe.title} to favorites", "success")
        return redirect(f"/recipe/{recipe.id}")

