from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI is running on Vercel!"}

@app.get("/game", response_class=HTMLResponse)
def game():
    try:
        with open("game/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Game not found</h1>", status_code=404)
