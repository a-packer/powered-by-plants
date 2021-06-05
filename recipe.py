import json
from models import db, Recipe

def add_structure_recipe(res):
    """takes response from API request and structures the return recipe info for db, returns recipe object"""

    response_string = res.text # get text from response
    response_dict = json.loads(response_string) #convert to json dict

    
    id = response_dict["id"]
    title = response_dict["title"]
    img = response_dict["image"]
    protein = response_dict["nutrition"]["nutrients"][9]["amount"]
    source_url = response_dict["sourceUrl"]

    ingredient_info = response_dict["extendedIngredients"] # list of ingredients with all the info
    ingredients = [] 
    for ing in ingredient_info: # make a list with just the amount, unit, name
        ingredients.append([ing["amount"], ing["unit"], ing["name"]])

    instructions = response_dict["analyzedInstructions"][0]["steps"]
    time = response_dict["readyInMinutes"]
    servings= response_dict["servings"]

    # import pdb; pdb.set_trace() 
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
