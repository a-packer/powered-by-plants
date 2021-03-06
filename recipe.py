import json
import requests
from models import db, Recipe


def add_structure_recipe(res):
    """takes response from API request and structures the return recipe info for db, returns recipe object"""

    response_string = res.text # get text from response
    response_dict = json.loads(response_string) #convert to json dict

    
    id = response_dict["id"]
    title = response_dict["title"]
    try:
        img = response_dict["image"]
    except KeyError:
        print("No image available")
        img = ""
    protein = response_dict["nutrition"]["nutrients"][9]["amount"]
    source_url = response_dict["sourceUrl"]

    ingredient_info = response_dict["extendedIngredients"] # list of ingredients with all the info
    ingredients = [] 
    for ing in ingredient_info: # make a list with just the amount, unit, name
        ingredients.append([ing["amount"], ing["unit"], ing["name"]])


    if len(response_dict["analyzedInstructions"]) != 0:
        instructions = response_dict["analyzedInstructions"][0]["steps"]
    else:
        instructions = {}
    time = response_dict["readyInMinutes"]
    servings= response_dict["servings"]

    
    # adds recipe to database
    recipe = Recipe.addRecipe(
        id=id,
        title=title,
        img=img,
        protein=protein,
        source_url=source_url,
        ingredients=json.dumps(ingredients), #converts to json
        instructions=json.dumps(instructions), #converts to json
        time=time,
        servings=servings
    )

    db.session.commit()

    return recipe



def gets_recipes(API_KEY, min_protein, intolerances, query):
    """Makes a request to spoonacular api for recipes based on query"""

    res = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&minProtein={min_protein}&intolerances={intolerances}&number=3&diet=vegan&query={query}&addRecipeInformation=True") 
    response_string = res.text
    response_dict = json.loads(response_string) #convert to json dict
    
    return response_dict

