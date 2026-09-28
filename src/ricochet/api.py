from fastapi import FastAPI, HTTPException
from ricochet.catalog import (list_table_names, get_table, 
                              list_game_names, get_game
                              )
from fastapi.middleware.cors import CORSMiddleware 

from ricochet.generator import random_table, random_game
from ricochet.table import Table 
from ricochet.game import Game 

app = FastAPI(title="Ricochet Robots API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # autorise toutes les origines (OK en développement)
    allow_methods=["*"],        # autorise GET, POST, etc.
    allow_headers=["*"],
)


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

# on garde en mémoire la dernière table générée, pour pouvoir
# créer une nouvelle partie sur la MÊME table
_last_random_table = None


@app.post("/generate/table")
def generate_table():
    """Génère une table aléatoire ET une première partie résoluble dessus."""
    global _last_random_table
    table = random_table()
    _last_random_table = table

    game = random_game(table)
    if game is None:
        raise HTTPException(status_code=500, detail="Aucune partie résoluble trouvée")

    return {"table": table.to_dict(), "game": game.to_dict()}


@app.post("/generate/game")
def generate_game():
    """Génère une nouvelle partie aléatoire sur la DERNIÈRE table générée."""
    global _last_random_table
    if _last_random_table is None:
        _last_random_table = random_table()

    game = random_game(_last_random_table)
    if game is None:
        raise HTTPException(status_code=500, detail="Aucune partie résoluble trouvée")

    return {"table": _last_random_table.to_dict(), "game": game.to_dict()}

from pydantic import BaseModel 
from ricochet.solvers import solve_bfs, solve_dijkstra, solve_astar

# --- Modèle décrivant ce que le navigateur envoie pour résoudre ---
class SolveRequest(BaseModel):
    table : dict    #table complète (to_dict)
    game: dict        # nom d'une partie du catalogue
    algorithm: str   # "bfs", "dijkstra" ou "astar"


# --- Table de correspondance nom -> fonction solveur ---
SOLVERS = {
    "bfs": solve_bfs,
    "dijkstra": solve_dijkstra,
    "astar": solve_astar,
}


@app.post("/solve")
def solve(request: SolveRequest):
    table = Table.from_dict(request.table)
    game = Game.from_dict(request.game, table)

    solver = SOLVERS.get(request.algorithm)
    if solver is None:
        raise HTTPException(status_code=400, detail=f"Algorithme inconnu : {request.algorithm}")

    solution = solver(game)
    if solution is None:
        return {"solved": False}

    return {
        "solved": True,
        "moves": solution.moves,
        "length": len(solution),
        "nodes_explored": solution.nodes_explored,
        "elapsed": solution.elapsed,
    }