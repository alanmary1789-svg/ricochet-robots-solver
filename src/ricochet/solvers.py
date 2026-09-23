from dataclasses import dataclass 
from ricochet.simulation import successors
from ricochet.table import Table 
from ricochet.game import Game, COLORS

from collections import deque
import heapq, itertools
import time

@dataclass
class Solution:
    moves : list 
    states : list
    nodes_explored : int 
    elapsed : int #temps de calcul en secondes 

    def __len__(self):
        return len(self.moves)

    """
    def solve_bfs(game):
        table = game.table
        depart, arrive = Game.start_state(game)[game.target_robot], (game.target_robot, game.target_cell)
        f, parent = [depart], {depart : None}
        while f != [] and not(arrive in parent):
            s = f[0]
            couples_coup_etat = successors(table, s)
            for couple in couples_coup_etat: 
                v, coup = couple[1], couple[0]
                if not (v in parent) :
                    parent[v] = (s,coup)
                    f.append(v)
                f = f.popleft() 
        if arrive in parent.keys():
            chemin = [(arrive, parent[arrive])]
            while chemin[-1][0] != depart :
                chemin.append(parent[chemin[-1][0]])
        return list.reversed(chemin)
    """
        
def solve_bfs(game):
        start = time.perf_counter() 

        depart = game.start_state()
        parent = {depart : None}    
        f = deque([depart])
        explored = 0

        if game.is_goal(depart):
            return _reconstruct(parent, depart, start, explored)

        while f : 
            s = f.popleft()
            explored += 1
            for coup, v in successors(game.table, s):
                if v not in parent:
                    parent[v] = (s, coup)

                    if game.is_goal(v):
                        return _reconstruct(parent, v, start, explored)
                    f.append(v)
        return None

def _reconstruct(parent, etat_final, start, explored):
        moves, states, noeud = [], [etat_final], etat_final
        while parent[noeud] is not None :
            precedent, coup = parent[noeud]
            moves.append(coup)
            states.append(precedent)
            noeud = precedent
        moves.reverse()
        states.reverse()

        return Solution(
            moves = moves, 
            states = states,
            nodes_explored = explored,
            elapsed = time.perf_counter() - start
        )

""" 
def solve_dijkstra(game):
    start = time.perf_counter()
    depart, parent, explored = game.start_state(), {depart : None}, 0
    tas, compteur, cout = [], itertools.count(), {depart : 0}
    heapq.heappush(tas, (0, next(compteur), depart))

    if game.is_goal(depart):
        return _reconstruct(parent, depart, start, explored)
    

    while tas : 
        u, state_u = heapq.heappop(tas)
        explored += 1 
        for coup, v in successors(game.table, u):
             if v not in parent:
                cout[v] = cout[u] + 1 
                parent[v] = (u, coup)

                if game.is_goal(v):
                     return _reconstruct_dijkstra(parent, v, start, explored)

                heapq.heappush(tas, (cout, etat))

    return None 
"""

def solve_dijkstra(game):
    start = time.perf_counter()

    depart = game.start_state()
    parent = {depart: None}
    cout = {depart: 0}
    compteur = itertools.count()
    tas = [(0, next(compteur), depart)]
    explored = 0

    while tas:
        cout_u, _, u = heapq.heappop(tas)
        if cout_u > cout[u]:          # entrée périmée : un meilleur chemin a déjà été traité
            continue
        explored += 1

        if game.is_goal(u):
            return _reconstruct(parent, u, start, explored)

        for coup, v in successors(game.table, u):
            nouveau_cout = cout[u] + 1
            if v not in cout or nouveau_cout < cout[v]:   # relâchement : chemin nouveau ou meilleur
                cout[v] = nouveau_cout
                parent[v] = (u, coup)
                heapq.heappush(tas, (nouveau_cout, next(compteur), v))

    return None



def _heuristique(game, state):
    """Minorant du nombre de coups restants : 0 si le robot cible est déjà
    sur la case, 1 s'il est aligné avec elle (même ligne ou même colonne),
    2 sinon. Toujours <= au vrai nombre de coups, donc admissible."""
    x, y = state[COLORS.index(game.target_robot)]
    tx, ty = game.target_cell
    if (x, y) == (tx, ty):
        return 0
    if x == tx or y == ty:
        return 1
    return 2


def solve_astar(game):
    start = time.perf_counter()

    depart = game.start_state()
    parent = {depart: None}
    cout = {depart: 0}
    compteur = itertools.count()
    tas = [(_heuristique(game, depart), next(compteur), depart)]
    explored = 0

    while tas:
        _, _, u = heapq.heappop(tas)
        if game.is_goal(u):
            return _reconstruct(parent, u, start, explored)
        explored += 1

        for coup, v in successors(game.table, u):
            nouveau_cout = cout[u] + 1
            if v not in cout or nouveau_cout < cout[v]:
                cout[v] = nouveau_cout
                parent[v] = (u, coup)
                priorite = nouveau_cout + _heuristique(game, v)   # f = g + h
                heapq.heappush(tas, (priorite, next(compteur), v))

    return None


def solve_bbfs(game):
        start = time.perf_counter() 

        depart, arrive = game.start_state(), (game.target_robot, game.target_cell)
        parent_1, parent_2 = {depart : None}, {arrive : None} #1 pour depart, 2 pour arrive
        f1, f2 = deque([depart]), deque([arrive])
        explored1, explored2 = 0, 0

        if game.is_goal(depart):
            return _reconstruct_bbfs(parent_1, depart, start, explored1)

        while f1 and f2 : 
            s1, s2 = f1.popleft(), f2.popleft

            explored1 += 1
            explored2 += 1

            for coup1, v1 in successors(game.table, s1):
                if v1 not in parent_1:
                    parent_1[v1] = (s1, coup1)

                    if game.is_goal(v1):
                        return _reconstruct(parent_1, v1, start, explored1)
                    f1.append(v1)

            for coup2, v2 in successors(game.table, s2):
                if v2 not in parent_1:
                    parent_2[v2] = (s2, coup2)
            
                    
                    f2.append(v2)
        return None
