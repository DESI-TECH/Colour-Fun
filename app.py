from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import os
import asyncio

app = FastAPI(title="Colour-Fun Backend")

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = Bot(token=BOT_TOKEN)

users = {}  # In-memory storage (replace with DB in production)

# -------------------
# Inline keyboard layout
# -------------------
keyboard_template = [
    [InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
     InlineKeyboardButton("🏧 Withdrawal", callback_data="withdrawal")],
    [InlineKeyboardButton("👤 Profile", callback_data="profile"),
     InlineKeyboardButton("📤 Share & Earn", callback_data="share")],
    [InlineKeyboardButton("🎮 Play", callback_data="play")]
]

# -------------------
# Telegram webhook
# -------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    text = data.get("message", {}).get("text", "")

    if text == "/start" and chat_id:
        if chat_id not in users:
            users[chat_id] = {"balance": 0, "points": 0, "transactions": []}
        await bot.send_message(
            chat_id=chat_id,
            text="Welcome to Colour-Fun! Choose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard_template)
        )

    return JSONResponse({"ok": True, "received": data})

# -------------------
# Serve game
# -------------------
@app.get("/game", response_class=HTMLResponse)
async def serve_game():
    path = "game/index.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Game not found</h1>", status_code=404)

@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI backend live!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
