from ricochet.table import Table 

def _demo_table():
    t = Table(8, 8, name="demo")
    t.add_wall(3, 0, "E")
    t.add_wall(5, 4, "S")
    t.add_wall(5, 4, "W")
    return t 


def _classic_table():
    t = Table(16, 16, name="classic")
    # quelques murs répartis sur le plateau (en L, comme le vrai jeu)
    walls = [
        (3, 1, "E"), (3, 1, "S"),
        (6, 2, "W"), (6, 2, "S"),
        (11, 3, "E"), (11, 3, "N"),
        (2, 5, "S"), (2, 5, "E"),
        (8, 6, "W"), (8, 6, "N"),
        (13, 7, "S"), (13, 7, "W"),
        (5, 9, "N"), (5, 9, "E"),
        (10, 10, "S"), (10, 10, "E"),
        (14, 11, "W"), (14, 11, "S"),
        (4, 13, "N"), (4, 13, "E"),
        (9, 14, "W"), (9, 14, "N"),
    ]
    for x, y, side in walls:
        t.add_wall(x, y, side)
    return t


TABLES = {
    "demo" : _demo_table(),
    "classic" : _classic_table(),
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

def _classic_game():
    return Game(
        table=TABLES["classic"],
        robots={"red": (0, 0), "green": (15, 15), "blue": (7, 0), "yellow": (0, 7)},
        target_robot="red",
        target_cell=(13, 11),
    )



GAMES = {
    "demo" : _demo_game(),
    "classic" : _classic_game(),
}

def list_game_names():
    return list(GAMES.keys())

def get_game(name):
    return  GAMES.get(name)

