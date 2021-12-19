import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BaseModel = declarative_base()


class Ingredient(BaseModel):
    __tablename__ = 'ingredients'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200))


class Recipe(BaseModel):
    __tablename__ = 'recipes'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(200))
    ingredients = relationship('Measurement', backref='recipe')
    steps = relationship('Step', backref='recipe')


class Measurement(BaseModel):
    __tablename__ = 'measurements'
    id = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Float)
    ingredient_id = sa.Column(sa.Integer, sa.ForeignKey(Ingredient.id))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey(Recipe.id))
    ingredient = relationship('Ingredient')


class Step(BaseModel):
    __tablename__ = 'steps'
    id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.SmallInteger)
    description = sa.Column(sa.String(2000))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey(Recipe.id))
