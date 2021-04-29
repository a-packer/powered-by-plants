from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)


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