import os

from flask import Flask, render_template, request, jsonify, session, g
import requests
import json
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

# TODO: add user signup and login forms
# from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Recipe, Favorite
from recipe import add_structure_recipe


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

    return jsonify(response_dict)  


@app.route("/recipe/<int:recipe_id>", methods=["POST"])
def add_recipe(recipe_id):
    """Adds recipe to db"""

    res = requests.get(f"https://api.spoonacular.com/recipes/324694/information?includeNutrition=True&apiKey=67de1636f65f4322adffda4851c70b9d")
    # response_string = res.text # get text from response
    # response_dict = json.loads(response_string) #convert to json dict
    # title = response_dict["title"]
    # img = response_dict["image"]
    # protein = response_dict["nutrition"]["nutrients"][9]["amount"]
    # api_id = response_dict["id"]
    # source_url = response_dict["sourceUrl"]
    # ingredient_info = response_dict["extendedIngredients"] # list of ingredients with all the info
    # ingredients = [] 
    # for ing in ingredient_info:            # make a list with just the amount, unit, name
    #     ingredients.append([ing["amount"], ing["unit"], ing["name"]])
    # instructions = response_dict["analyzedInstructions"][0]["steps"]
    # time = response_dict["readyInMinutes"]
    # servings= response_dict["servings"]

    # recipe = Recipe.addRecipe(
    #     title=title,
    #     img=img,
    #     protein=protein,
    #     api_id=api_id,
    #     source_url=source_url,
    #     ingredients=json.dumps(ingredients), #converts to json
    #     instructions=json.dumps(instructions), #converts to json
    #     time=time,
    #     servings=servings
    # )

    # db.session.commit()

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
                password=form.password.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


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

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged Out", 'danger')

    return redirect('/')


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user

    form = UserAddForm(obj=user)

    if form.validate_on_submit():
        try:
            user.username=form.username.data


            user.email=form.email.data,
            user.image_url=form.image_url.data 

            user = User.authenticate(form.username.data,
                                    form.password.data)

            if user:
                db.session.commit()
                
                do_login(user)
                flash(f"Hello, {user.username}!", "success")
                return render_template('users/detail.html', user=user)

            flash("Invalid credentials.", 'danger')
            return redirect("/")
            

        except IntegrityError:
            flash("Username already taken", 'danger')
            return redirect("/")
       
        return render_template('users/profile.html', form=form)

    else:
        return render_template('users/edit.html', form=form)
    

    

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


@app.route('/users/add_like/<int:message_id>', methods=["GET", "POST"])
def add_like(message_id):
    """Add a 'like' to a message"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)
    message = Message.query.get_or_404(message_id)

    # check to see if message in liked messages already. If not, add to likes
    liked_messages = user.likes
    likes = [liked_message.id for liked_message in liked_messages]
    if message.id in likes:
        likes.remove(message.id)
        user.likes = [Message.query.get(like_id) for like_id in likes]
        db.session.commit()
        return redirect('/')
    else:
        user.likes.append(message)
        db.session.commit()
        return redirect('/')