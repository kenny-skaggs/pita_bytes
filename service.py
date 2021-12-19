
from external import Database
import models


class Storage:
    @classmethod
    def create_recipe(cls, name: str, ingredients, steps):
        recipe = models.Recipe(
            name=name,
            ingredients=[
                models.Measurement(
                    amount=measure['measure'],
                    ingredient=models.Ingredient(name=measure['name'])
                )
                for measure in ingredients
            ],
            steps=[models.Step(description=step, number=number) for number, step in enumerate(steps)]
        )
        with Database().get_new_session() as session:
            session.add(recipe)

    @classmethod
    def load_recipes(cls):
        with Database().get_new_session() as session:
            return session.query(models.Recipe).all()

    @classmethod
    def load_recipe(cls, recipe_id):
        with Database().get_new_session() as session:
            return session.query(models.Recipe).filter(models.Recipe.id == recipe_id).one()
