import time

from flask import Flask, render_template, request, url_for

import view_models
from service import Storage

app = Flask(__name__)


@app.route('/')
def home():
    recipes = Storage.load_recipes()
    return render_template('home.html', recipes=recipes)


@app.route('/recipe/<recipe_id>')
def show_recipe(recipe_id):
    recipe = Storage.load_recipe(recipe_id=recipe_id)
    return render_template('recipe_view.html', recipe=recipe)


@app.route('/new')
def new_recipe():
    return render_template('recipe_edit.html', recipe=None)


@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    request_json = request.json
    recipe = view_models.Recipe(
        id_=request_json['recipe_id'],
        name=request_json['name'],
        source=request_json['source'],
        steps=request_json['steps'],
        ingredients=[
            view_models.Ingredient(
                name=ingredient_json['name'],
                unit=ingredient_json['unit'],
                amount=ingredient_json['amount'],
                preparation=ingredient_json['preparation']
            )
            for ingredient_json in request_json['ingredients']
        ]
    )
    recipe_id = Storage.upsert_recipe(recipe)
    return url_for('show_recipe', recipe_id=recipe_id)


@app.route('/recipe/<recipe_id>/edit')
def edit_recipe(recipe_id):
    recipe = Storage.load_recipe(recipe_id=recipe_id)
    return render_template('recipe_edit.html', recipe=recipe)
