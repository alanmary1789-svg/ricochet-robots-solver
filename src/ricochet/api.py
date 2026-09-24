from fastapi import FastAPI

app = FastAPI(title="Ricochet Robots API")


@app.get("/ping")
def ping():
    return {"message": "pong"}