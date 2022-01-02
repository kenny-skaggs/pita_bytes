from dataclasses import dataclass, field
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
    tags: List[str] = field(default_factory=list)
    id_: int = None
