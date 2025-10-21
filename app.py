from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import os

# --------------------------
# FASTAPI APP (must be named 'app')
# --------------------------
app = FastAPI(title="Colour-Fun Backend")

# --------------------------
# ENV VARIABLES / BOT TOKEN
# --------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
GAME_HTML_PATH = "game/index.html"

# --------------------------
# ROOT ROUTE
# --------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI backend is running on Vercel!"}

# --------------------------
# SERVE GAME PAGE
# --------------------------
@app.get("/game", response_class=HTMLResponse)
def serve_game():
    try:
        with open(GAME_HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Game not found</h1>", status_code=404)

# --------------------------
# TELEGRAM BOT WEBHOOK (placeholder)
# --------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    # TODO: Process Telegram updates here (Deposit, Withdrawal, Profile, Play buttons)
    return JSONResponse({"ok": True, "received": data})

# --------------------------
# HEALTH CHECK
# --------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}
