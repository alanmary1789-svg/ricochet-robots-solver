from ricochet.table import Table
from dataclasses import dataclass

COLORS = ("red", "green", "blue", "yellow")

@dataclass

class Game: 
    table : Table 
    robots : dict[str, tuple[int, int]]
    target_robot : str
    target_cell : tuple[int, int] 

    def start_state(self):
        return tuple(self.robots[color] for color in COLORS)

    def is_goal(self, state):
        return state[COLORS.index(self.target_robot)] == self.target_cell

    def validate(self):
        positions = {self.robots[color] for color in COLORS}
        if len(positions) != 4 : 
            raise ValueError("Deux robots sont sur la même position")
        for color in COLORS:
            x, y = self.robots[color]
            if not self.table.in_bounds(x, y):
                raise ValueError(f"Le robot {color} hors des limites")

        tx, ty = self.target_cell
        if not self.table.in_bounds(tx, ty):
            raise ValueError("La cellule cible est hors des limites")

        if self.target_robot not in COLORS:
            raise ValueError(f"Robot cible inconnue : {self.target_robot}")

    def to_dict(self):
        return {"table" : self.table.name, 
                "robots" : {c : list(self.robots[c]) for c in COLORS}, 
                "target_robot" : self.target_robot, 
                "target_cell" : list(self.target_cell)
                }


    @classmethod
    def from_dict(cls, data, table):
        robots = {c : tuple(pos) for c, pos in data["robots"].items()}
        return cls(table = table,
                   robots = robots, 
                   target_robot = data["target_robot"], 
                   target_cell = tuple(data["target_cell"]))

    