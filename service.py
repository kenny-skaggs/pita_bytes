from typing import List

from sqlalchemy.orm import joinedload
from sympy import Eq, solve, symbols
from sympy.parsing.sympy_parser import parse_expr

from external import Database
import models
import view_models


class Storage:
    @classmethod
    def upsert_recipe(cls, recipe_data: view_models.Recipe):
        ingredients = [
            models.Measurement(
                amount=AmountConverter.serialize_value(str(ingredient.amount)),
                unit=ingredient.unit,
                ingredient=models.Ingredient(name=ingredient.name),  # TODO: look up ingredient by name
                preparation=ingredient.preparation
            )
            for ingredient in recipe_data.ingredients
        ]
        steps = [models.Step(description=step, number=number) for number, step in enumerate(recipe_data.steps)]

        with Database().get_new_session() as session:
            if recipe_data.id_:
                recipe = session.query(models.Recipe).filter(models.Recipe.id == recipe_data.id_).one()
            else:
                recipe = models.Recipe()

            recipe.name = recipe_data.name
            recipe.source = recipe_data.source
            recipe.ingredients = ingredients
            recipe.steps = steps

            if not recipe_data.id_:
                session.add(recipe)

        return recipe.id

    @classmethod
    def load_recipes(cls) -> List[view_models.Recipe]:
        with Database().get_new_session() as session:
            recipes = session.query(models.Recipe).all()
            return [cls._get_vm_recipe(recipe) for recipe in recipes]

    @classmethod
    def load_recipe(cls, recipe_id) -> view_models.Recipe:
        with Database().get_new_session() as session:
            recipe = session.query(
                models.Recipe
            ).filter(
                models.Recipe.id == recipe_id
            ).options(
                joinedload(models.Recipe.ingredients).joinedload(models.Measurement.ingredient),
                joinedload(models.Recipe.steps)
            ).one()
            return cls._get_vm_recipe(recipe)

    @classmethod
    def _get_vm_recipe(cls, recipe: models.Recipe) -> view_models.Recipe:
        steps = [step.description for step in recipe.steps]
        ingredients = [
            view_models.Ingredient(
                name=measurement.ingredient.name,
                amount=AmountConverter.deserialize_value(measurement.amount),
                unit=measurement.unit,
                preparation=measurement.preparation
            )
            for measurement in recipe.ingredients
        ]
        return view_models.Recipe(
            id_=recipe.id,
            name=recipe.name,
            source=recipe.source,
            ingredients=ingredients,
            steps=steps
        )


class AmountConverter:
    """
    Helps transform between display strings for ingredient measurements (like 1/3) to database storable
    values (like 0.333).
    """

    @classmethod
    def serialize_value(cls, amount: str) -> float:
        return float(parse_expr(amount).evalf())

    @classmethod
    def deserialize_value(cls, amount: float) -> str:
        x, y, z = symbols('x y z')
        expression = Eq(x/y, z)
        for denominator in range(1, 25):
            numerator = solve(expression.subs({
                y: denominator,
                z: amount
            }))[0].evalf()
            if abs(numerator - round(numerator)) <= 0.01:
                integer_numerator = round(numerator)
                if denominator == 1:
                    return str(integer_numerator)
                else:
                    return f'{integer_numerator}/{denominator}'

        return 'conversion error'
