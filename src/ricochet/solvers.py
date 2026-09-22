from dataclasses import dataclass 
from ricochet.simulation import successors
from ricochet.table import Table 
from ricochet.game import Game 

from collections import deque
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


