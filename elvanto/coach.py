from abc import ABC

"""
IDEA
----

Graph
-----
Head Coach
         |
-------------------
|        |        |
Coach    Coach    Coach
|
-------------------- ... ---
|        |        |        |
Lead     Lead     Lead     Lead
|
----------
|        |
CG       Team


Attributes
----------
Coach
> .parents  = [head_coach1, head_coach2, ...]
> .children = [coach1, coach2, coach3, ...]
> .leads  = [cgroup1, cgroup2, cgroup3, ...]
"""


class Coach(ABC):
    def __init__(self, name: str, parents=[], children=[]):
        self.name = name
        self.parents = set(parents)
        self.children = set(children)
        super().__init__()

    def update(self, parents, children):
        self.parents  |= set(parents)
        self.children |= set(children)
        return self

    @classmethod
    def from_dict(cls, data):
        return cls(**data)