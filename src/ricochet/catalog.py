from ricochet.table import Table 

def _demo_table():
    t = Table(8, 8, name="demo")
    t.add_wall(3, 0, "E")
    t.add_wall(5, 4, "S")
    t.add_wall(5, 4, "W")
    return t 

TABLES = {
    "demo" : _demo_table(),
}

def list_table_names():
    """Renvoie la liste des noms de tables disponibles."""
    return list(TABLES.keys())

def get_table(name):
    """Renvoie la Table de ce nom, ou None si elle n'existe pas."""
    return TABLES.get(name)

from ricochet.game import Game 

def _demo_game():
    return Game(
        table = TABLES["demo"],
        robots = {"red": (0, 0), "green": (7, 7), "blue": (3, 7), "yellow": (7, 3)},
        target_robot = "red",
        target_cell = (3, 6)
    )

GAMES = {
    "demo" : _demo_game(),
}

def list_game_names():
    return list(GAMES.keys())

def get_game(name):
    return  GAMES.get(name)

