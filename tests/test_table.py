from ricochet.table import Table 

def test_wall_is_symmetric():
    t = Table(5, 5)
    t.add_wall(2,0,"E")
    assert t.has_wall(2,0,"E")
    assert t.has_wall(3,0,"W")


def test_in_bounds():
    t = Table(5, 5)
    t.add_wall(2,0,"E")

    assert t.in_bounds(0, 0)
    assert t.in_bounds(4, 4)

    assert not t.in_bounds(-1, 0)
    assert not t.in_bounds(5, 0)

def test_no_walls_where_none_added():
    t = Table(5, 5)
    assert not t.has_wall(0, 0, "N")

def test_add_wall_near_boarder_has_no_mirror():
    t = Table(5, 5)
    t.add_wall(4, 0, "E")
    assert t.has_wall(4, 0, "E")
    assert not t.has_wall(5, 0 , "W")
    assert len(t.walls) == 1 

def test_round_trip_dict():
    t = Table(5, 5, name =  "essai") 
    t.add_wall(2, 0, "E")
    t.add_wall(1, 3, "S")

    rebuilt = Table.from_dict(t.to_dict())

    assert rebuilt.width == t.width and rebuilt.height == t.height and rebuilt.name == t.name and rebuilt.walls == t.walls 


