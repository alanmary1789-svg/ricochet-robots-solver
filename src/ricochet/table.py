from dataclasses import dataclass, field 

DIRECTIONS = {"N" : (0,-1), "S" : (0,1), "E" : (1,0), "W" : (-1,0)}
OPPOSITE = {"N" : "S", "S" : "N", "E" : "W", "W" : "E"}

@dataclass 
class Table:
    width : int 
    height : int
    walls : set[tuple[int, int, str]] = field(default_factory=set)
    name : str = ""

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height 

    def add_wall(self, x, y, side):
        self.walls.add((x, y, side))
        dir = DIRECTIONS[side]
        if Table.in_bounds(self,x + dir[0], y + dir[1]):
            self.walls.add((x + dir[0], y + dir[1], OPPOSITE[side]))

    def has_wall(self, x, y, side):
        return (x, y, side) in self.walls

    def to_dict(self):
        return {"name" : self.name, "width" : self.width, "height" : self.height, "walls" : [list(wall) for wall in self.walls]}


    @classmethod
    def from_dict(cls, data):
        table = cls(data["width"], data["height"], name = data.get("name", ""))
        for mur in data["walls"]:
            table.add_wall(mur[0], mur[1], mur[2])

        return table


