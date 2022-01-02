from typing import Collection, List

from sqlalchemy.orm import joinedload, Session
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
        tag_names = [tag_name.lower() for tag_name in recipe_data.tags]

        with Database().get_new_session() as session:
            existing_tags = cls._load_existing_tags(tag_names, session)
            new_tags = [
                models.Tag(name=tag_name)
                for tag_name in tag_names
                if not any([tag_obj.name == tag_name for tag_obj in existing_tags])
            ]

            if recipe_data.id_:
                recipe = session.query(models.Recipe).filter(models.Recipe.id == recipe_data.id_).one()
                # clear all tags related to the recipe right now
                session.query(models.RecipeTag).filter(models.RecipeTag.recipe_id == recipe.id).delete()
            else:
                recipe = models.Recipe()

            recipe.name = recipe_data.name
            recipe.source = recipe_data.source
            recipe.ingredients = ingredients
            recipe.steps = steps

            recipe.tags = [
                models.RecipeTag(recipe=recipe, tag=tag_obj)
                for tag_obj in [*existing_tags, *new_tags]
            ]

            if not recipe_data.id_:
                session.add(recipe)

        return recipe.id

    @classmethod
    def _load_existing_tags(cls, tags: List[str], session: Session) -> Collection[models.Tag]:
        return session.query(models.Tag).filter(
            models.Tag.name.in_(tags)
        ).all()

    @classmethod
    def load_recipes(cls) -> List[view_models.Recipe]:
        with Database().get_new_session() as session:
            recipes = session.query(models.Recipe).options(
                joinedload(models.Recipe.ingredients).joinedload(models.Measurement.ingredient)
            ).all()
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
        tags = [recipe_tag.tag.name for recipe_tag in recipe.tag_refs]
        return view_models.Recipe(
            id_=recipe.id,
            name=recipe.name,
            source=recipe.source,
            ingredients=ingredients,
            steps=steps,
            tags=tags
        )


class AmountConverter:
    """
    Helps transform between display strings for ingredient measurements (like 1/3) to database storable
    values (like 0.333).
    """

    @classmethod
    def serialize_value(cls, amount: str) -> float:
        from sympy.parsing.sympy_parser import auto_number

        def mixed_numbers(tokens, _, __):
            if len(tokens) == 6:  # mixed number
                numerator_token = tokens[1]
                denominator_token = tokens[3]

                new_numerator_val = int(tokens[0][1]) * int(denominator_token[1]) + int(numerator_token[1])
                return [(numerator_token[0], str(new_numerator_val)), tokens[2], denominator_token, *tokens[4:]]
            else:
                return tokens

        return float(parse_expr(amount, transformations=(mixed_numbers, auto_number)).evalf())

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
                    return cls._eval_as_mixed_number(integer_numerator, denominator)

        raise Exception('conversion failed')

    @classmethod
    def _eval_as_mixed_number(cls, numerator: int, denominator: int) -> str:
        if numerator / denominator > 1:
            return f'{numerator // denominator} {numerator % denominator}/{denominator}'
        else:
            return f'{numerator}/{denominator}'

