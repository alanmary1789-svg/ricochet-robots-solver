"""Génération aléatoire de tables et de parties (validées par un solveur)."""
import random

from ricochet.table import Table, DIRECTIONS
from ricochet.game import Game, COLORS
from ricochet.solvers import solve_bfs

def add_center_block(table):
    """Entoure de murs les 4 cases centrales d'un plateau de taille paire,
    les rendant inaccessibles (comme le bloc central du vrai jeu)."""
    cx = table.width // 2 - 1   # ex: 16 -> 7
    cy = table.height // 2 - 1
    # les 4 cases du bloc central
    block = {(cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1)}
    # pour chaque case du bloc, on mure les côtés qui donnent vers l'extérieur
    for (x, y) in block:
        for side, (dx, dy) in DIRECTIONS.items():
            neighbor = (x + dx, y + dy)
            if neighbor not in block:      # côté extérieur au bloc
                table.add_wall(x, y, side)


def center_cells(table):
    """Renvoie l'ensemble des 4 cases centrales (inaccessibles) d'un 16x16,
    ou un ensemble vide si le plateau n'a pas de bloc central."""
    if table.width == 16 and table.height == 16:
        cx = table.width // 2 - 1
        cy = table.height // 2 - 1
        return {(cx, cy), (cx + 1, cy), (cx, cy + 1), (cx + 1, cy + 1)}
    return set()


def random_table(width=16, height=16, n_walls=18, name="random"):
    """Crée une table avec des murs placés aléatoirement à l'intérieur."""
    t = Table(width, height, name=name)
    if width == 16 and height == 16:
        add_center_block(t)
    sides = list(DIRECTIONS)
    for _ in range(n_walls):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        side = random.choice(sides)
        t.add_wall(x, y, side)
    return t


def random_game(table, max_tries=100):
    """Place robots, robot cible et case d'arrivée au hasard sur `table`,
    et ne renvoie qu'une partie RÉSOLUBLE. Renvoie None si aucune trouvée."""
    forbidden = center_cells(table)
    cells = [(x, y) for x in range(table.width) for y in range(table.height)
             if (x, y) not in forbidden]

    for _ in range(max_tries):
        # 4 cases distinctes pour les robots + 1 pour l'arrivée
        picks = random.sample(cells, 5)
        robots = {color: picks[i] for i, color in enumerate(COLORS)}
        target_robot = random.choice(COLORS)
        target_cell = picks[4]

        game = Game(
            table=table,
            robots=robots,
            target_robot=target_robot,
            target_cell=target_cell,
        )

        # on garde la partie seulement si elle est résoluble
        if solve_bfs(game) is not None:
            return game

    return None