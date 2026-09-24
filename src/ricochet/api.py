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

