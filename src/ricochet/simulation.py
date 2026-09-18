from ricochet.table import Table, DIRECTIONS
from ricochet.game import COLORS

def slide(table, start, direction, occupied):
    x, y = start
    dx, dy = DIRECTIONS[direction]
    b = False
    while not b :
        if table.has_wall(x, y, direction) or ((x + dx, y + dy) in occupied) or not table.in_bounds(x + dx, y + dy):
            b = True 
        else:
            x += dx
            y += dy
    return (x, y)


def successors(table, state):
    couples = set()
    for i in range(4):
        occupied = {state[j] for j in range(4) if j != i}
        for direction in DIRECTIONS:
            nouvelle_case = slide(table, state[i], direction, occupied)
            nouvel_etat = state[:i] + (nouvelle_case,) + state[i+1:]
            if nouvelle_case != state[i]:
                couples.add(((i, direction), nouvel_etat))
    return couples 
