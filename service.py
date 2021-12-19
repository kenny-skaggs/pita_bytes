
from sqlalchemy.orm import joinedload

from external import Database
import models


class Storage:
    @classmethod
    def upsert_recipe(cls, recipe_id: int, name: str, ingredients, steps):
        ingredients = [
            models.Measurement(
                amount=measure['amount'],
                unit=measure['unit'],
                ingredient=models.Ingredient(name=measure['name']),
                preparation=measure['preparation']
            )
            for measure in ingredients
        ]
        steps = [models.Step(description=step, number=number) for number, step in enumerate(steps)]

        if recipe_id:
            recipe = cls.load_recipe(recipe_id)
        else:
            recipe = models.Recipe()

        recipe.name = name
        recipe.ingredients = ingredients
        recipe.steps = steps
        with Database().get_new_session() as session:
            session.merge(recipe)

    @classmethod
    def load_recipes(cls):
        with Database().get_new_session() as session:
            return session.query(models.Recipe).all()

    @classmethod
    def load_recipe(cls, recipe_id):
        with Database().get_new_session() as session:
            return session.query(
                models.Recipe
            ).filter(
                models.Recipe.id == recipe_id
            ).options(
                joinedload(models.Recipe.ingredients).joinedload(models.Measurement.ingredient),
                joinedload(models.Recipe.steps)
            ).one()
