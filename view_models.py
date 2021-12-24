from dataclasses import dataclass
from typing import List


@dataclass
class Ingredient:
    name: str
    amount: str
    unit: str
    preparation: str = None


@dataclass
class Recipe:
    name: str
    source: str
    ingredients: List[Ingredient]
    steps: List[str]
    id_: int = None
