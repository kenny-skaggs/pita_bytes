
from flask import Flask, render_template, request

from service import Storage

app = Flask(__name__)


@app.route('/')
def home():
    recipes = Storage.load_recipes()
    return render_template('home.html', recipes=recipes)


@app.route('/new')
def new_recipe():
    return render_template('recipe_edit.html', recipe=None)


@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    request_json = request.json
    Storage.upsert_recipe(
        recipe_id=request_json['recipe_id'],
        name=request_json['name'],
        ingredients=request_json['ingredients'],
        steps=request_json['steps']
    )
    return request_json


@app.route('/recipe/<recipe_id>')
def show_recipe(recipe_id):
    recipe = Storage.load_recipe(recipe_id=recipe_id)
    return render_template('recipe_view.html', recipe=recipe)


@app.route('/recipe/<recipe_id>/edit')
def edit_recipe(recipe_id):
    recipe = Storage.load_recipe(recipe_id=recipe_id)
    return render_template('recipe_edit.html', recipe=recipe)
