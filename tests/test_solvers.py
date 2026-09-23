from ricochet.solvers import Solution 
from ricochet.table import Table 
from ricochet.game import Game, COLORS
from ricochet.solvers import solve_bfs, solve_dijkstra, solve_astar 

import pytest 

def test_solution_len():
    sol = Solution(
        moves = [(0, "E"), (0,"S")],
        states = [(1, 2),(3, 4),(5, 6)],
        nodes_explored = 10,
        elapsed = 0.01

    )

    assert len(sol) == 2


def make_game(target_cell, robots= None):
    table = Table(5, 5, name="t")
    robots  = robots or {"red" : (0, 0), "green" : (0, 4), "blue" : (4, 4), "yellow" : (2, 4)}
    return Game(table = table, robots = robots, target_robot = "red", target_cell = target_cell)

def test_bfs_already_won():
    g = make_game(target_cell=(0, 0))     # rouge est déjà en (0,0)
    sol = solve_bfs(g)
    assert sol is not None and len(sol) == 0


def test_bfs_one_move():
    g = make_game(target_cell=(4, 0))     # rouge glisse vers l'est jusqu'au bord
    sol = solve_bfs(g)
    assert sol is not None and len(sol) == 1
    assert sol.moves[0] == (0, "E")


def test_bfs_states_length_invariant():
    g = make_game(target_cell=(4, 0))
    sol = solve_bfs(g)
    assert len(sol.states) == len(sol.moves) + 1   # invariante états/coups


def test_bfs_unreachable():
    table = Table(5, 5, name="t")
    for side in ("N", "S", "E", "W"):
        table.add_wall(1, 1, side)        # case (1,1) murée de partout
    g = Game(table=table,
             robots={"red": (0, 0), "green": (0, 4), "blue": (4, 4), "yellow": (2, 4)},
             target_robot="red", target_cell=(1, 1))
    assert solve_bfs(g) is None

def test_solvers_agree_on_length():
    g = make_game(target_cell=(4, 0))
    n_bfs = len(solve_bfs(g))
    assert len(solve_dijkstra(g)) == n_bfs
    assert len(solve_astar(g)) == n_bfs


def test_dijkstra_and_astar_unreachable():
    table = Table(5, 5, name="t")
    for side in ("N", "S", "E", "W"):
        table.add_wall(1, 1, side)
    g = Game(table=table,
             robots={"red": (0, 0), "green": (0, 4), "blue": (4, 4), "yellow": (2, 4)},
             target_robot="red", target_cell=(1, 1))
    assert solve_dijkstra(g) is None
    assert solve_astar(g) is None

