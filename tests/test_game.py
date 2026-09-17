import pytest
from ricochet.table import Table
from ricochet.game import Game, COLORS

def make_game():
    table = Table(8, 8, name = "t1")
    return Game(
        table = table,
        robots = {"red" : (0, 0), "green" : (7, 7),"blue" : (3, 7),"yellow" : (7, 3)},
        target_robot = "red",
        target_cell = (3,6)
    )

def test_start_state_order():
    g = make_game()
    assert g.start_state() == ((0,0), (7,7), (3,7), (7,3))

def test_is_goal_true_and_false():
    g = make_game()
    assert not g.is_goal(g.start_state())
    won = ((3, 6), (7, 7), (3, 7), (7, 3))
    assert g.is_goal(won)


def test_validate_ok():
    g = make_game()
    g.validate()

def test_validate_two_robots_same_cell():
    g = make_game()
    g.robots["green"] = (0, 0)
    with pytest.raises(ValueError):
        g.validate()

def test_validate_robot_out_of_bounds():
    g = make_game()
    g.robots["blue"] = (99, 99)
    with pytest.raises(ValueError):
        g.validate()

def test_roundtrip_dict():
    g = make_game()
    data = g.to_dict()
    rebuilt = Game.from_dict(data, g.table)

    assert rebuilt.robots == g.robots
    assert rebuilt.target_robot == g.target_robot
    assert rebuilt.target_cell == g.target_cell
    assert data["table"] == "t1" 
