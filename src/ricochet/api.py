from fastapi import FastAPI, HTTPException
from ricochet.catalog import (list_table_names, get_table, 
                              list_game_names, get_game
                              )
app = FastAPI(title="Ricochet Robots API")


@app.get("/ping")
def ping():
    return {"message": "pong"}      


@app.get("/tables")
def tables():
    """Liste les noms des tables dispnibles."""
    return {"tables" : list_table_names()}


@app.get("/tables/{name}")
def table(name: str):
    """Renvoie une table précise (ses murs) au format JSON."""
    t = get_table(name)
    if t is None :
        raise HTTPException(status_code = 404, detail = f"Table inconnue : {name}")
    return t.to_dict()


@app.get("/games")
def games():
    """Listes les noms des parties disponibles."""
    return {"games": list_game_names()}

@app.get("/games/{name}")
def game(name: str):
    """Renvoie une partie précise (robots, cible, arrivée) au format JSON."""
    g = get_game(name)
    if g is None:
        raise HTTPException(status_code=404, detail = f"Partie inconnue : {name}")
    return g.to_dict()

from pydantic import BaseModel 
from ricochet.solvers import solve_bfs, solve_dijkstra, solve_astar

# --- Modèle décrivant ce que le navigateur envoie pour résoudre ---
class SolveRequest(BaseModel):
    game: str        # nom d'une partie du catalogue
    algorithm: str   # "bfs", "dijkstra" ou "astar"


# --- Table de correspondance nom -> fonction solveur ---
SOLVERS = {
    "bfs": solve_bfs,
    "dijkstra": solve_dijkstra,
    "astar": solve_astar,
}


@app.post("/solve")
def solve(request: SolveRequest):
    """Résout une partie avec l'algorithme demandé, renvoie coups + statistiques."""
    g = get_game(request.game)
    if g is None:
        raise HTTPException(status_code=404, detail=f"Partie inconnue : {request.game}")

    solver = SOLVERS.get(request.algorithm)
    if solver is None:
        raise HTTPException(status_code=400, detail=f"Algorithme inconnu : {request.algorithm}")

    solution = solver(g)
    if solution is None:
        return {"solved": False}

    return {
        "solved": True,
        "moves": solution.moves,
        "length": len(solution),
        "nodes_explored": solution.nodes_explored,
        "elapsed": solution.elapsed,
    }