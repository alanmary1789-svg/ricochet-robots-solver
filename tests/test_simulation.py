from ricochet.table import Table 
from ricochet.simulation import slide
from ricochet.simulation import successors
import pytest 


""" === TEST DEPLACEMENT === """
def test_slide_to_east_border(): 
    t = Table(5, 5)
    assert slide(t, (0, 0), "E", set()) == (4, 0)

def test_slide_to_south_border():
    t = Table(5, 5)
    assert slide(t, (0, 0), "S", set()) == (0, 4)

def test_slide_stops_before_robot():
    t = Table(5, 5)
    assert slide(t, (0, 0), "E", {(3,0)}) == (2,0)

def test_slide_stops_at_wall():
    t = Table(5, 5)
    t.add_wall(2, 0, "E")
    assert slide(t, (0, 0), "E", set()) == (2, 0)

def test_slide_stops_at_wall_from_other_side():
    t = Table(5, 5)
    t.add_wall(2, 0, "E")
    assert slide(t, (4, 0), "W", set()) == (3, 0) 

def test_slide_no_move_when_against_border():
    t = Table(5, 5)
    assert slide(t, (0, 0), "W", set()) == (0, 0)

def test_slide_no_move_when_against_robot():
    t = Table(5, 5)
    assert slide(t, (2, 0), "E", {(3, 0)}) == (2,0)



""" === TEST SUCCESSORS === """

def test_successor_changes_one_robot():
    t = Table(5, 5)
    state = ((0, 0), (4, 4), (0, 4), (4, 0))
    for coup, nouvel_etat in successors(t, state):
        i = coup[0]
        # seul le robot d'indice i a bougé ; les autres sont identiques
        for k in range(4):
            if k == i:
                assert nouvel_etat[k] != state[k]
            else:
                assert nouvel_etat[k] == state[k]


def test_successor_robot_blocks_robot():
    t = Table(5, 5)
    # rouge en (0,0), vert en (3,0) : rouge vers l'est s'arrête en (2,0)
    state = ((0, 0), (3, 0), (0, 4), (4, 4))
    d = dict(successors(t, state))
    assert (0, "E") in d
    assert d[(0, "E")][0] == (2, 0)   # position du robot 0 dans le nouvel état


def test_successor_blocked_move_absent():
    t = Table(5, 5)
    # rouge dans le coin (0,0) : il ne peut aller ni au nord ni à l'ouest
    state = ((0, 0), (4, 4), (0, 4), (4, 0))
    d = dict(successors(t, state))
    assert (0, "N") not in d
    assert (0, "W") not in d